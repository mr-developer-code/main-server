cloudflared login
	# select domain
cloudflared tunnel create sgi-server-tunnel
nano ~/.cloudflared/config_server.yml

	tunnel: sgi-server-tunnel
	credentials-file: /home/YOUR_USERNAME/.cloudflared/file_name.json

	ingress:
	  - hostname: serverpost.huzaifa.cloud
	    service: http://localhost:4353
	  - hostname: serverget.huzaifa.cloud
	    service: http://localhost:3035
	  - service: http_status:404

cloudflared tunnel route dns sgi-server-tunnel serverpost.huzaifa.cloud
cloudflared tunnel route dns sgi-server-tunnel serverget.huzaifa.cloud

sudo mkdir -p /etc/cloudflared
sudo cp ~/.cloudflared/*.yml /etc/cloudflared/
sudo cp ~/.cloudflared/*.json /etc/cloudflared/

# change .json path in .yml file

sudo cp /home/coder/Desktop/securegenai/server/main-server.service /etc/systemd/system/main-server.service

sudo cp /home/coder/Desktop/securegenai/server/main-cloudflared.service /etc/systemd/system/main-cloudflared.service

sudo /bin/systemctl daemon-reload
sudo /bin/systemctl daemon-reexec

sudo /bin/systemctl enable main-server.service
sudo /bin/systemctl start main-server.service

sudo /bin/systemctl enable main-cloudflared.service
sudo /bin/systemctl start main-cloudflared.service

----------------------------------------------------------------------------------
cloudflared tunnel --config ~/.cloudflared/config_api.yml run