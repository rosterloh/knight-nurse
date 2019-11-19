#!/bin/bash
DELAY=2
POSITIONAL_ARGS=()

SERVICE_PATH=/etc/systemd/system/knight-nurse.service

USAGE="sudo ./install-service.sh --delay <n>"

while [[ $# -gt 0 ]]; do
        K="$1"
	case $K in
        -d|--delay)
		DELAY="$2"
		shift
		shift
		;;
        *)
		if [[ $1 == -* ]]; then
			printf "Unrecognised option: $1\n";
			printf "Usage: $USAGE\n";
			exit 1
		fi
		POSITIONAL_ARGS+=("$1")
		shift
	esac
done

set -- "${POSITIONAL_ARGS[@]}"

cat << EOF
Setting up with:
Delay:          $DELAY seconds
To change these options, run:
$USAGE
Or edit: $SERVICE_PATH


EOF

read -r -d '' UNIT_FILE << EOF
[Unit]
Description=Knight Nurse Service
After=multi-user.target

[Service]
Type=simple
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/monitor.py --delay $DELAY
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

printf "\nInstalling service to: $SERVICE_PATH\n"
echo "$UNIT_FILE" > $SERVICE_PATH
systemctl daemon-reload
systemctl enable --no-pager knight-nurse.service
systemctl restart --no-pager knight-nurse.service
systemctl status --no-pager knight-nurse.service