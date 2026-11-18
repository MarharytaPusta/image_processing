import os
import time
import logging
import requests
import docker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("image_processing")

NODES = [
    {"address": "web1:8000", "optional": False},
    {"address": "web2:8000", "optional": False},
    {"address": "192.168.0.122:8000", "optional": True},
]

UPSTREAM_CONFIG_PATH = "/etc/nginx/dynamic/upstream.conf"
CHECK_INTERVAL = 5
MAX_FAILS = 2
COOLDOWN_SECONDS = 300

node_state = {
    node["address"]: {"fails": 0, "cooldown_until": 0.0, "offline_logged": False}
    for node in NODES
}


def calculate_weight(metrics: dict) -> int:
    cpu = metrics.get("cpu", 50.0)
    ram = metrics.get("ram", 50.0)

    load_score = (cpu * 0.7) + (ram * 0.3)

    weight = round(10 - (load_score / 10))
    return max(1, min(10, weight))


def generate_upstream_config() -> str:
    lines = ["upstream django_cluster {", "    least_conn;"]
    now = time.time()

    for node in NODES:
        addr = node["address"]
        extra_flags = " max_fails=3 fail_timeout=30s" if node["optional"] else ""
        state = node_state[addr]

        if now < state["cooldown_until"]:
            lines.append(f"    server {addr} weight=1{extra_flags};")
            continue

        try:
            response = requests.get(f"http://{addr}/metrics/", timeout=1.5)
            response.raise_for_status()
            data = response.json()

            if state["offline_logged"] or state["fails"] > 0:
                logger.info(f"[METRICS] {addr}: connection restored")

            state["fails"] = 0
            state["cooldown_until"] = 0.0
            state["offline_logged"] = False

            weight = calculate_weight(data)
            logger.info(
                f"[METRICS] {addr} ({data.get('server')}): "
                f"CPU={data['cpu']}%, RAM={data['ram']}% -> weight={weight}"
            )
        except Exception:
            state["fails"] += 1
            weight = 1

            if state["fails"] >= MAX_FAILS:
                state["cooldown_until"] = now + COOLDOWN_SECONDS
                if not state["offline_logged"]:
                    logger.warning(
                        f"[METRICS] {addr}: node unreachable, switching to standby (weight=1)"
                    )
                    state["offline_logged"] = True

        lines.append(f"    server {addr} weight={weight}{extra_flags};")

    lines.append("}")
    return "\n".join(lines) + "\n"


def reload_nginx(docker_client):
    containers = docker_client.containers.list(
        filters={"label": "com.docker.compose.service=nginx"}
    )
    if containers:
        containers[0].exec_run("nginx -s reload")
        logger.info("[NGINX] Upstream configuration updated (nginx -s reload)")
    else:
        logger.error("[NGINX] Error: nginx container not found")


def main():
    os.makedirs(os.path.dirname(UPSTREAM_CONFIG_PATH), exist_ok=True)
    docker_client = docker.from_env()
    last_config = ""

    while True:
        new_config = generate_upstream_config()

        if new_config != last_config:
            with open(UPSTREAM_CONFIG_PATH, "w", encoding="utf-8") as f:
                f.write(new_config)
            reload_nginx(docker_client)
            last_config = new_config

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()