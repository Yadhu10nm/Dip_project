import argparse
import sys
import config

def main():
    parser = argparse.ArgumentParser(
        description="AI Security CCTV — Unauthorized Intruder Detection & Access Control System"
    )
    parser.add_argument(
        "--mode",
        choices=["web", "desktop"],
        default="web",
        help="Interface mode: 'web' (default browser dashboard) or 'desktop' (OpenCV window)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Web server port (default: 5000)"
    )
    parser.add_argument(
        "--camera",
        type=int,
        default=config.CAMERA_INDEX,
        help=f"Camera index (default: {config.CAMERA_INDEX})"
    )

    args = parser.parse_args()
    config.CAMERA_INDEX = args.camera

    if args.mode == "web":
        from web.app import run_server
        run_server(port=args.port)
    else:
        from desktop_app import run_desktop_app
        run_desktop_app()

if __name__ == "__main__":
    main()
