import sys
import logging

from manifest.ui import ManifestUI

LOGGER = logging.getLogger(__name__)


def main():
    try:
        # Create and launch UI
        LOGGER.info("Launching Gradio interface...")
        UI = ManifestUI()
        UI.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            show_error=True
        )

    except FileNotFoundError as e:
        LOGGER.error(f"Configuration file not found: {e}")
        print("❌ Error: config.yaml not found. Please create it first.")
        sys.exit(1)

    except Exception as e:
        LOGGER.error(f"Error starting application: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()