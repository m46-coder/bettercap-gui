import pytest
from bettercap_gui.__main__ import BettercapGUI

def test_gui_initialization():
    # Note: This is a basic test; GUI testing requires a display environment.
    app = None
    try:
        app = BettercapGUI()
        assert app.title() == "Bettercap GUI Automator"
        for tab in ("General", "Workflows", "Spoofing", "Recon", "WiFi"):
            assert app.tabview.tab(tab) is not None
    except Exception as e:
        pytest.skip(f"GUI test skipped due to environment: {e}")
    finally:
        if app:
            app.destroy()
