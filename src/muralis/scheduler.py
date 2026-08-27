"""Scheduler management for Muralis auto-updates."""

import subprocess
import sys
from pathlib import Path

from muralis.i18n import t

SYSTEMD_SERVICE_TEMPLATE = """[Unit]
Description=Muralis - Daily Wallpaper Update
Documentation=https://github.com/quoxiom/muralis
After=network.target

[Service]
Type=oneshot
ExecStart={script_path} --once
User={user}
Environment="DISPLAY=:0"
Environment="DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/{uid}/bus"
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""

SYSTEMD_TIMER_TEMPLATE = """[Unit]
Description=Muralis Daily Wallpaper Timer
Documentation=https://github.com/quoxiom/muralis
Requires=muralis.service

[Timer]
OnCalendar=*-*-* {time}:00
Persistent=true
RandomizedDelaySec=1800

[Install]
WantedBy=timers.target
"""

CRON_TEMPLATE = "# Muralis daily wallpaper update\n{minute} {hour} * * * {script_path} --once\n"


class SchedulerManager:
    """Manages automatic wallpaper updates."""

    def __init__(self, config):
        self.config = config
        self.auto_update = self.config.get_bool("general", "auto_update", True)
        self.update_time = self.config.get_update_time() or "09:00"

    def setup(self) -> bool:
        """Setup automatic updates using systemd or cron."""
        # Try systemd first (modern Linux)
        if self._setup_systemd():
            return True

        # Fallback to cron
        if self._setup_cron():
            return True
        return False

    def disable(self) -> bool:
        """Remove the background daily timer/job (systemd first, then cron)."""
        removed = False
        # systemd user timer
        timer_path = Path.home() / ".config/systemd/user/muralis.timer"
        service_path = Path.home() / ".config/systemd/user/muralis.service"
        if timer_path.exists() or service_path.exists():
            try:
                subprocess.run(
                    ["systemctl", "--user", "disable", "--now", "muralis.timer"],
                    check=False,
                    capture_output=True,
                )
                if timer_path.exists():
                    timer_path.unlink()
                if service_path.exists():
                    service_path.unlink()
                subprocess.run(
                    ["systemctl", "--user", "daemon-reload"], check=False, capture_output=True
                )
                removed = True
            except Exception:
                pass
        # cron fallback
        try:
            result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
            lines = result.stdout.splitlines() if result.returncode == 0 else []
            filtered = [ln for ln in lines if "muralis" not in ln]
            if len(filtered) != len(lines):
                subprocess.run(
                    ["crontab", "-"], input="\n".join(filtered) + "\n", text=True, check=False
                )
                removed = True
        except Exception:
            pass
        return removed

    def _hour_minute(self) -> tuple:
        """Parse the configured update time (HH:MM) into (hour, minute)."""
        hour, minute = 9, 0
        try:
            parts = self.update_time.split(":")
            hour = int(parts[0])
            minute = int(parts[1]) if len(parts) > 1 else 0
        except (ValueError, AttributeError):
            pass
        return max(0, min(23, hour)), max(0, min(59, minute))

    def _setup_systemd(self) -> bool:
        """Setup systemd user timer."""
        try:
            # Find script path
            script_path = self._get_script_path()

            user = subprocess.check_output(["whoami"], text=True).strip()
            uid = subprocess.check_output(["id", "-u"], text=True).strip()

            # Create service file
            service_content = SYSTEMD_SERVICE_TEMPLATE.format(
                script_path=script_path, user=user, uid=uid
            )

            service_path = Path.home() / ".config/systemd/user/muralis.service"
            service_path.parent.mkdir(parents=True, exist_ok=True)
            service_path.write_text(service_content)

            # Create timer file (uses the configured update time)
            hour, minute = self._hour_minute()
            timer_content = SYSTEMD_TIMER_TEMPLATE.format(time=f"{hour:02d}:{minute:02d}")
            timer_path = Path.home() / ".config/systemd/user/muralis.timer"
            timer_path.write_text(timer_content)

            # Enable and start timer
            subprocess.run(
                ["systemctl", "--user", "daemon-reload"], check=True, capture_output=True
            )
            subprocess.run(
                ["systemctl", "--user", "enable", "muralis.timer"], check=True, capture_output=True
            )
            subprocess.run(
                ["systemctl", "--user", "start", "muralis.timer"], check=True, capture_output=True
            )

            print(t("cli.sched.systemd_ok"))
            return True

        except Exception as e:
            print(t("cli.sched.systemd_fail", error=e))
            return False

    def _setup_cron(self) -> bool:
        """Setup cron job as fallback."""
        try:
            script_path = self._get_script_path()
            hour, minute = self._hour_minute()
            cron_line = CRON_TEMPLATE.format(script_path=script_path, hour=hour, minute=minute)

            # Check if crontab exists
            result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
            current_cron = result.stdout if result.returncode == 0 else ""

            # Add our line if not present
            if "muralis" not in current_cron:
                new_cron = current_cron + "\n" + cron_line
                subprocess.run(["crontab", "-"], input=new_cron, text=True, check=True)
                print(t("cli.sched.cron_ok"))
                return True

            return True

        except Exception as e:
            print(t("cli.sched.cron_fail", error=e))
            return False

    def _get_script_path(self) -> str:
        """Get path to muralis script."""
        # Check common locations
        possible_paths = [
            str(Path(sys.argv[0]).absolute()),
            str(Path.home() / ".local/bin/muralis"),
            "/usr/local/bin/muralis",
            "/usr/bin/muralis",
        ]

        for path in possible_paths:
            if Path(path).exists():
                return path

        # Return current script path as fallback
        return str(Path(sys.argv[0]).absolute())

    def start(self, run_callback=None):
        """Run a blocking scheduler loop for non-systemd/cron systems.

        Runs a wallpaper update immediately, then every ``interval`` seconds.
        ``run_callback`` is a zero-arg callable that performs the update (e.g.
        ``MuralisApp.run_once``); if omitted, the loop just reports each cycle.
        """
        import time

        if not self.auto_update:
            print(t("cli.sched.auto_disabled"))
            return

        interval = self.config.get_int("general", "update_interval", 86400)
        print(t("cli.sched.auto_enabled", hours=interval // 3600))

        while True:
            if run_callback:
                try:
                    run_callback()
                except Exception as e:
                    print(t("cli.sched.cycle_error", error=e))
            else:
                print(t("cli.sched.cycle"))
            time.sleep(interval)
