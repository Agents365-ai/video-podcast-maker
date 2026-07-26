from __future__ import annotations

import argparse
import ipaddress

from .api import create_server
from .service import ProductionCoordinator
from .store import ProductionStore
from .workers import WorkerGateway


def _loopback_host(value: str) -> str:
    if value == "localhost":
        return value
    try:
        address = ipaddress.ip_address(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("host must be loopback") from error
    if not address.is_loopback:
        raise argparse.ArgumentTypeError("host must be loopback")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the local Video Production Coordinator",
    )
    parser.add_argument("--host", type=_loopback_host, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8791)
    parser.add_argument("--database", required=True)
    args = parser.parse_args()

    store = ProductionStore(args.database)
    coordinator = ProductionCoordinator(store, WorkerGateway())
    server = create_server(args.host, args.port, coordinator)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        store.close()


if __name__ == "__main__":
    main()
