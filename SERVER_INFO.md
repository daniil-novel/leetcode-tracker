```xml
<?xml version="1.0" encoding="UTF-8"?>
<ServerKnowledgeBase>
    <ServerInfo>
        <Provider>VDSina.ru</Provider>
        <IP>91.84.104.36</IP>
        <OS>Ubuntu 22.04 LTS</OS>
        <Hostname>v353999</Hostname>
        <Location>Russia</Location>
        <Purpose>Outline VPN Server + Web Hosting</Purpose>
    </ServerInfo>

    <SSH_Access>
        <Connection>
            <Method>SSH Key Authentication</Method>
            <Command>ssh root@91.84.104.36</Command>
            <Port>22</Port>
            <User>root</User>
            <Note>Passwordless SSH configured with key-based auth</Note>
        </Connection>
        
        <SSH_Key_Setup>
            <LocalKeyPath>~/.ssh/id_rsa (Windows: C:\Users\USERNAME\.ssh\id_rsa)</LocalKeyPath>
            <PublicKeyOnServer>/root/.ssh/authorized_keys</PublicKeyOnServer>
            <Permissions>
                <AuthorizedKeys>600</AuthorizedKeys>
                <SSHDirectory>700</SSHDirectory>
            </Permissions>
        </SSH_Key_Setup>
    </SSH_Access>

    <Passwords>
        <RootPassword>
            <Status>Disabled (SSH key only)</Status>
            <OriginalPassword>Not stored (security)</OriginalPassword>
        </RootPassword>
        
        <MySQLRootPassword>
            <Value>ENCRYPTED_IN_HISTORY</Value>
            <Note>Set during MySQL installation, check /root/.mysql_history</Note>
        </MySQLRootPassword>
    </Passwords>

    <Domain>
        <Name>novel-cloudtech.com</Name>
        <Aliases>www.novel-cloudtech.com</Aliases>
        <SSL_Certificate>
            <Type>Let's Encrypt</Type>
            <Issuer>Certbot</Issuer>
            <AutoRenewal>Enabled via cron</AutoRenewal>
            <Ports>
                <HTTP>80 (redirects to HTTPS)</HTTP>
                <HTTPS>7443</HTTPS>
            </Ports>
        </SSL_Certificate>
        
        <WebRoot>/var/www/novel-cloudtech.com</WebRoot>
        <NginxConfig>/etc/nginx/sites-enabled/novel-cloudtech.com</NginxConfig>
    </Domain>

    <OutlineVPN>
        <Status>Active and Optimized</Status>
        
        <Installation>
            <Method>Docker-based installation</Method>
            <InstallCommand>sudo bash -c "$(wget -qO- https://raw.githubusercontent.com/Jigsaw-Code/outline-server/master/src/server_manager/install_scripts/install_server.sh)"</InstallCommand>
        </Installation>

        <Configuration>
            <ManagerURL>https://91.84.104.36:55515/t4XpSsBVXRc8CQep7Le4Qg</ManagerURL>
            <APIEndpoint>https://127.0.0.1:55515/t4XpSsBVXRc8CQep7Le4Qg</APIEndpoint>
            <ManagementPort>55515</ManagementPort>
            <CertFingerprint>t4XpSsBVXRc8CQep7Le4Qg</CertFingerprint>
        </Configuration>

        <AccessKeys>
            <KeyFile>/root/outline_keys_optimized.txt</KeyFile>
            <Users>
                <User id="1" name="Pasha-Makarov"/>
                <User id="2" name="Alena-Dolinka"/>
                <User id="3" name="Vlad-Privezentsev"/>
                <User id="4" name="Alena-Smirnova"/>
                <User id="5" name="Daniil-Privezentsev"/>
                <User id="6" name="Papus"/>
                <User id="7" name="Tisha"/>
                <User id="8" name="reserve1"/>
                <User id="9" name="reserve2"/>
                <User id="10" name="reserve3"/>
            </Users>
            <Note>All keys stored in outline_keys_optimized.txt with full access URLs</Note>
        </AccessKeys>

        <Docker>
            <Container>
                <Name>shadowbox</Name>
                <Image>quay.io/outline/shadowbox:stable</Image>
                <Status>Running</Status>
                <RestartPolicy>Always</RestartPolicy>
                <Commands>
                    <Restart>sudo docker restart shadowbox</Restart>
                    <Logs>sudo docker logs shadowbox</Logs>
                    <Status>sudo docker ps | grep shadowbox</Status>
                </Commands>
            </Container>
            
            <WatchtowerContainer>
                <Name>watchtower</Name>
                <Image>containrrr/watchtower</Image>
                <Purpose>Auto-update Outline container</Purpose>
            </WatchtowerContainer>
        </Docker>

        <NetworkOptimizations>
            <TelegramBypass>
                <Status>Active</Status>
                <Description>Telegram traffic bypasses VPN on server side</Description>
                
                <TelegramIPRanges>
                    <Range>149.154.160.0/20</Range>
                    <Range>149.154.164.0/22</Range>
                    <Range>149.154.168.0/22</Range>
                    <Range>149.154.172.0/22</Range>
                    <Range>91.108.4.0/22</Range>
                    <Range>91.108.8.0/22</Range>
                    <Range>91.108.12.0/22</Range>
                    <Range>91.108.16.0/22</Range>
                    <Range>91.108.20.0/22</Range>
                    <Range>91.108.56.0/22</Range>
                    <Range>95.161.64.0/20</Range>
                </TelegramIPRanges>

                <RoutingTable>
                    <Name>telegram_direct</Name>
                    <ID>200</ID>
                    <ConfigFile>/etc/iproute2/rt_tables</ConfigFile>
                </RoutingTable>

                <IPTablesRules>
                    <Chain>TELEGRAM_BYPASS</Chain>
                    <Table>mangle</Table>
                    <Mark>200</Mark>
                </IPTablesRules>

                <AutostartScript>
                    <Path>/opt/telegram-server-bypass.sh</Path>
                    <Service>/etc/systemd/system/telegram-server-bypass.service</Service>
                    <Status>Enabled and running</Status>
                </AutostartScript>
            </TelegramBypass>

            <YouTubeInstagramOptimization>
                <Description>Optimized for video streaming</Description>
                <SysctlSettings>
                    <Setting name="net.core.rmem_default">262144</Setting>
                    <Setting name="net.core.rmem_max">16777216</Setting>
                    <Setting name="net.core.wmem_default">262144</Setting>
                    <Setting name="net.core.wmem_max">16777216</Setting>
                    <Setting name="net.ipv4.tcp_rmem">4096 87380 16777216</Setting>
                    <Setting name="net.ipv4.tcp_wmem">4096 65536 16777216</Setting>
                    <Setting name="net.core.netdev_budget">600</Setting>
                    <Setting name="net.core.netdev_max_backlog">5000</Setting>
                </SysctlSettings>
                <ConfigFile>/etc/sysctl.conf</ConfigFile>
            </YouTubeInstagramOptimization>
        </NetworkOptimizations>
    </OutlineVPN>

    <WebServer>
        <Nginx>
            <Version>Latest stable</Version>
            <Status>Active</Status>
            
            <Configuration>
                <MainConfig>/etc/nginx/nginx.conf</MainConfig>
                <SitesAvailable>/etc/nginx/sites-available/</SitesAvailable>
                <SitesEnabled>/etc/nginx/sites-enabled/</SitesEnabled>
                <CurrentSite>/etc/nginx/sites-enabled/novel-cloudtech.com</CurrentSite>
            </Configuration>

            <VirtualHost>
                <ServerName>novel-cloudtech.com www.novel-cloudtech.com</ServerName>
                <DocumentRoot>/var/www/novel-cloudtech.com</DocumentRoot>
                <HTTPPort>80</HTTPPort>
                <HTTPSPort>7443</HTTPSPort>
                <SSL>
                    <Certificate>/etc/letsencrypt/live/novel-cloudtech.com/fullchain.pem</Certificate>
                    <PrivateKey>/etc/letsencrypt/live/novel-cloudtech.com/privkey.pem</PrivateKey>
                </SSL>
                <HTTPRedirect>Redirects all HTTP to HTTPS on port 7443</HTTPRedirect>
            </VirtualHost>

            <Commands>
                <Test>sudo nginx -t</Test>
                <Reload>sudo systemctl reload nginx</Reload>
                <Restart>sudo systemctl restart nginx</Restart>
                <Status>sudo systemctl status nginx</Status>
            </Commands>
        </Nginx>

        <CurrentWebsite>
            <Location>/var/www/html</Location>
            <Type>Static HTML</Type>
            <Owner>www-data:www-data</Owner>
            <Permissions>755</Permissions>
        </CurrentWebsite>
    </WebServer>

    <SystemServices>
        <Docker>
            <Status>Active</Status>
            <AutoStart>Enabled</AutoStart>
            <Commands>
                <Start>sudo systemctl start docker</Start>
                <Stop>sudo systemctl stop docker</Stop>
                <Restart>sudo systemctl restart docker</Restart>
                <Status>sudo systemctl status docker</Status>
            </Commands>
        </Docker>

        <TelegramBypass>
            <Service>telegram-server-bypass.service</Service>
            <Status>Active and enabled</Status>
            <Script>/opt/telegram-server-bypass.sh</Script>
            <Commands>
                <Start>sudo systemctl start telegram-server-bypass</Start>
                <Restart>sudo systemctl restart telegram-server-bypass</Restart>
                <Status>sudo systemctl status telegram-server-bypass</Status>
            </Commands>
        </TelegramBypass>

        <Nginx>
            <Service>nginx.service</Service>
            <Status>Active and enabled</Status>
            <Commands>
                <Start>sudo systemctl start nginx</Start>
                <Stop>sudo systemctl stop nginx</Stop>
                <Reload>sudo systemctl reload nginx</Reload>
                <Status>sudo systemctl status nginx</Status>
            </Commands>
        </Nginx>
    </SystemServices>

    <FileSystem>
        <ImportantDirectories>
            <Directory path="/var/www/html">Default web root</Directory>
            <Directory path="/var/www/novel-cloudtech.com">Domain-specific web root</Directory>
            <Directory path="/etc/nginx">Nginx configuration</Directory>
            <Directory path="/etc/letsencrypt">SSL certificates</Directory>
            <Directory path="/root/.ssh">SSH keys</Directory>
            <Directory path="/opt">Custom scripts (telegram bypass)</Directory>
        </ImportantDirectories>

        <ImportantFiles>
            <File path="/root/outline_keys_optimized.txt">All Outline VPN access keys</File>
            <File path="/etc/nginx/sites-enabled/novel-cloudtech.com">Nginx site config</File>
            <File path="/etc/sysctl.conf">Network optimization settings</File>
            <File path="/etc/iproute2/rt_tables">Routing tables (telegram_direct)</File>
            <File path="/opt/telegram-server-bypass.sh">Telegram bypass autostart script</File>
        </ImportantFiles>
    </FileSystem>

    <NetworkConfiguration>
        <MainInterface>ens3</MainInterface>
        <DefaultGateway>91.84.104.1</DefaultGateway>
        <PublicIP>91.84.104.36</PublicIP>
        
        <OpenPorts>
            <Port number="22">SSH</Port>
            <Port number="80">HTTP (redirects to 7443)</Port>
            <Port number="7443">HTTPS</Port>
            <Port number="55515">Outline Management</Port>
            <Port number="Various UDP">Outline VPN traffic</Port>
        </OpenPorts>

        <Firewall>
            <Type>iptables</Type>
            <CustomChains>
                <Chain name="TELEGRAM_BYPASS" table="mangle">Telegram traffic bypass</Chain>
            </CustomChains>
        </Firewall>
    </NetworkConfiguration>

    <MaintenanceCommands>
        <SystemUpdates>
            <UpdatePackages>sudo apt update &amp;&amp; sudo apt upgrade -y</UpdatePackages>
            <CleanOldPackages>sudo apt autoremove -y</CleanOldPackages>
        </SystemUpdates>

        <OutlineManagement>
            <ViewAllKeys>curl -k -s "https://127.0.0.1:55515/t4XpSsBVXRc8CQep7Le4Qg/access-keys/" | python3 -m json.tool</ViewAllKeys>
            <CreateKey>curl -k -s -X POST "https://127.0.0.1:55515/t4XpSsBVXRc8CQep7Le4Qg/access-keys/" -H "Content-Type: application/json" -d '{"name": "USERNAME"}'</CreateKey>
            <DeleteKey>curl -k -s -X DELETE "https://127.0.0.1:55515/t4XpSsBVXRc8CQep7Le4Qg/access-keys/KEY_ID"</DeleteKey>
        </OutlineManagement>

        <LogViewing>
            <NginxAccessLog>sudo tail -f /var/log/nginx/access.log</NginxAccessLog>
            <NginxErrorLog>sudo tail -f /var/log/nginx/error.log</NginxErrorLog>
            <OutlineLogs>sudo docker logs -f shadowbox</OutlineLogs>
            <SystemLog>sudo journalctl -xe</SystemLog>
        </LogViewing>

        <NetworkDiagnostics>
            <CheckRoutes>ip route show</CheckRoutes>
            <CheckTelegramRoutes>ip route get 149.154.160.1</CheckTelegramRoutes>
            <CheckIPTables>sudo iptables -t mangle -L TELEGRAM_BYPASS -n</CheckIPTables>
            <CheckOpenPorts>sudo netstat -tulpn</CheckOpenPorts>
        </NetworkDiagnostics>
    </MaintenanceCommands>

    <DeploymentProcedures>
        <NewWebsiteDeployment>
            <Step1>Backup current site: sudo cp -r /var/www/html /var/www/html.backup</Step1>
            <Step2>Upload new files to /var/www/novel-cloudtech.com</Step2>
            <Step3>Set permissions: sudo chown -R www-data:www-data /var/www/novel-cloudtech.com</Step3>
            <Step4>Test nginx config: sudo nginx -t</Step4>
            <Step5>Reload nginx: sudo systemctl reload nginx</Step5>
        </NewWebsiteDeployment>

        <FileUploadMethods>
            <SCP>scp -r /local/path root@91.84.104.36:/var/www/novel-cloudtech.com</SCP>
            <SFTP>sftp root@91.84.104.36</SFTP>
            <Git>cd /var/www/novel-cloudtech.com &amp;&amp; git pull</Git>
        </FileUploadMethods>
    </DeploymentProcedures>

    <TroubleshootingGuide>
        <Issue name="Outline VPN not working">
            <Check1>sudo docker ps | grep shadowbox - check if container running</Check1>
            <Check2>sudo docker logs shadowbox - check for errors</Check2>
            <Solution>sudo docker restart shadowbox</Solution>
        </Issue>

        <Issue name="Website not accessible">
            <Check1>sudo systemctl status nginx</Check1>
            <Check2>sudo nginx -t - test configuration</Check2>
            <Check3>Check firewall: sudo ufw status</Check3>
            <Solution>sudo systemctl restart nginx</Solution>
        </Issue>

        <Issue name="Telegram still using VPN">
            <Check1>ip route get 149.154.160.1 - should show direct route</Check1>
            <Check2>sudo systemctl status telegram-server-bypass</Check2>
            <Solution>sudo systemctl restart telegram-server-bypass</Solution>
        </Issue>

        <Issue name="SSL certificate issues">
            <Check1>sudo certbot certificates</Check1>
            <Solution>sudo certbot renew --force-renewal</Solution>
        </Issue>
    </TroubleshootingGuide>

    <BackupRecommendations>
        <Critical>
            <Item>/root/outline_keys_optimized.txt - VPN access keys</Item>
            <Item>/etc/nginx/sites-enabled/ - Nginx configuration</Item>
            <Item>/var/www/ - Website files</Item>
            <Item>/root/.ssh/authorized_keys - SSH access</Item>
            <Item>/opt/telegram-server-bypass.sh - Custom scripts</Item>
        </Critical>
        
        <BackupCommand>
            sudo tar -czf backup-$(date +%Y%m%d).tar.gz /var/www /etc/nginx /root/outline_keys_optimized.txt /opt/telegram-server-bypass.sh
        </BackupCommand>
    </BackupRecommendations>

    <SecurityNotes>
        <SSH>
            <PasswordAuth>Disabled</PasswordAuth>
            <RootLogin>Permitted (key-based only)</RootLogin>
            <Port>22 (standard)</Port>
        </SSH>

        <Firewall>
            <Status>Active (iptables)</Status>
            <AllowedPorts>22, 80, 7443, 55515, UDP for Outline</AllowedPorts>
        </Firewall>

        <SSL>
            <Protocol>TLS 1.2+</Protocol>
            <AutoRenewal>Enabled via certbot</AutoRenewal>
        </SSL>
    </SecurityNotes>

    <KnownIssuesAndSolutions>
        <Issue>
            <Problem>Telegram showed "Connecting..." constantly</Problem>
            <Cause>Telegram traffic was going through VPN</Cause>
            <Solution>Implemented server-side bypass with iptables and routing tables</Solution>
            <Status>Resolved</Status>
        </Issue>

        <Issue>
            <Problem>Initial Outline setup on non-standard port</Problem>
            <Cause>Port 443 already used by website</Cause>
            <Solution>Outline installed on port 55515 instead</Solution>
            <Status>Working as intended</Status>
        </Issue>
    </KnownIssuesAndSolutions>

    <FutureConsiderations>
        <Item>Deploy new project on novel-cloudtech.com domain</Item>
        <Item>Possible migration from static HTML to dynamic application</Item>
        <Item>Monitor Outline VPN performance and optimize as needed</Item>
        <Item>Regular security updates and patches</Item>
    </FutureConsiderations>
</ServerKnowledgeBase>
```