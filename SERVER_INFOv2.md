<?xml version="1.0" encoding="UTF-8"?>
<ServerKnowledgeBase version="2.0">
    <ServerInfo>
        <Provider>VDSina.ru</Provider>
        <IP>91.84.104.36</IP>
        <OS>Ubuntu 22.04 LTS</OS>
        <Hostname>v353999</Hostname>
        <Location>Russia</Location>
        <Purpose>Outline VPN Server + Web Hosting (LeetCode Tracker FastAPI Application)</Purpose>
    </ServerInfo>

    <SSH_Access>
        <Connection>
            <Method>SSH Key Authentication (Preferred)</Method>
            <MethodAlternative>Password Authentication</MethodAlternative>
            <Commands>
                <KeyBased>ssh root@91.84.104.36</KeyBased>
                <KeyBasedHostname>ssh root@v353999.hosted-by-vdsina.com</KeyBasedHostname>
            </Commands>
            <Port>22</Port>
            <User>root</User>
        </Connection>
        
        <Credentials>
            <Username>root</Username>
            <Password>123123123123123123123123123123Aa!</Password>
            <Note>Passwordless SSH configured with key-based auth, but password auth also available</Note>
        </Credentials>

        <SSH_Key_Setup>
            <LocalKeyPath>~/.ssh/id_rsa (Windows: C:\Users\USERNAME\.ssh\id_rsa)</LocalKeyPath>
            <PublicKeyOnServer>/root/.ssh/authorized_keys</PublicKeyOnServer>
            <Permissions>
                <AuthorizedKeys>600</AuthorizedKeys>
                <SSHDirectory>700</SSHDirectory>
            </Permissions>
        </SSH_Key_Setup>

        <ConnectionExamples>
            <Windows>
                <PowerShell>ssh root@v353999.hosted-by-vdsina.com</PowerShell>
                <PuTTY>
                    <Host>v353999.hosted-by-vdsina.com</Host>
                    <Port>22</Port>
                    <Username>root</Username>
                    <Password>123123123123123123123123123123Aa!</Password>
                </PuTTY>
            </Windows>
            <Linux_Mac>ssh root@v353999.hosted-by-vdsina.com</Linux_Mac>
        </ConnectionExamples>
    </SSH_Access>

    <Domain>
        <Name>novel-cloudtech.com</Name>
        <Aliases>www.novel-cloudtech.com</Aliases>
        <SSL_Certificate>
            <Type>Let's Encrypt</Type>
            <Issuer>Certbot</Issuer>
            <AutoRenewal>Enabled via cron</AutoRenewal>
            <Ports>
                <HTTP>80 (redirects to HTTPS)</HTTP>
                <HTTP_Custom>8888 (redirects to HTTPS:7443)</HTTP_Custom>
                <HTTPS>7443 (main application port)</HTTPS>
                <HTTPS_Standard>443 (redirects to 7443)</HTTPS_Standard>
            </Ports>
        </SSL_Certificate>
        
        <WebRoot>/var/www/novel-cloudtech.com</WebRoot>
        <NginxConfig>/etc/nginx/sites-enabled/novel-cloudtech.com</NginxConfig>
        <ApplicationURL>https://novel-cloudtech.com:7443</ApplicationURL>
    </Domain>

    <LeetCodeTrackerApplication>
        <Description>FastAPI web application for gamified LeetCode progress tracking</Description>
        <Version>1.0.0</Version>
        <Repository>https://github.com/daniil-novel/leetcode-tracker.git</Repository>
        <CurrentBranch>main</CurrentBranch>
        <LatestCommit>4d37a96 - Complete project state after fixing all issues and adding new features</LatestCommit>

        <ProjectStructure>
            <Location>/root/leetcode_tracker_uv</Location>
            <Files>
                <File>pyproject.toml - UV project configuration and dependencies</File>
                <File>uv.lock - Locked dependencies</File>
                <File>README.md - Project documentation</File>
                <File>leetcode.db - SQLite database with user data</File>
                <Directory>leetcode_tracker/ - Main application code</Directory>
                <Directory>.venv/ - Python virtual environment</Directory>
                <Directory>.git/ - Git repository</Directory>
            </Files>
        </ProjectStructure>

        <Technology>
            <Backend>
                <Framework>FastAPI 0.121.3</Framework>
                <ORM>SQLAlchemy 2.0.44</ORM>
                <Server>Uvicorn 0.38.0</Server>
                <Database>SQLite (leetcode.db)</Database>
                <PackageManager>uv 0.9.11</PackageManager>
                <Python>3.10.12</Python>
            </Backend>
            <Frontend>
                <Templates>Jinja2 3.1.6</Templates>
                <Styling>Tailwind CSS (via CDN)</Styling>
                <Charts>Chart.js (via CDN)</Charts>
                <Interactivity>Alpine.js, HTMX</Interactivity>
            </Frontend>
        </Technology>

        <Dependencies>
            <Package name="fastapi" version="0.121.3"/>
            <Package name="uvicorn" version="0.38.0"/>
            <Package name="sqlalchemy" version="2.0.44"/>
            <Package name="pydantic" version="2.12.4"/>
            <Package name="jinja2" version="3.1.6"/>
            <Package name="python-dotenv" version="1.2.1"/>
            <Package name="python-multipart" version="0.0.20"/>
            <Package name="httptools" version="0.7.1"/>
            <Package name="uvloop" version="0.22.1"/>
            <Package name="watchfiles" version="1.1.1"/>
            <Package name="websockets" version="15.0.1"/>
            <!-- See uv.lock for complete dependency list -->
        </Dependencies>

        <ServiceConfiguration>
            <ServiceFile>/etc/systemd/system/leetcode-tracker.service</ServiceFile>
            <ServiceName>leetcode-tracker.service</ServiceName>
            <User>root</User>
            <WorkingDirectory>/root/leetcode_tracker_uv</WorkingDirectory>
            <ExecStart>/root/.local/bin/uv run uvicorn leetcode_tracker.main:app --host 127.0.0.1 --port 8000</ExecStart>
            <Restart>always</Restart>
            <RestartSec>10</RestartSec>
            <AutoStart>enabled</AutoStart>
            <Port>8000 (localhost only)</Port>
        </ServiceConfiguration>

        <Features>
            <Feature>Add solved LeetCode problems with XP (Easy=1, Medium=3, Hard=5)</Feature>
            <Feature>SQLite database storage</Feature>
            <Feature>Interactive charts (Chart.js): problems per day, XP per day, cumulative XP, streak tracking</Feature>
            <Feature>Recent problems table</Feature>
            <Feature>Monthly XP goal tracking</Feature>
            <Feature>Detailed month statistics with calendar view</Feature>
            <Feature>Time spent tracking for tasks</Feature>
            <Feature>CSV import functionality (supports aggregate and detailed formats)</Feature>
            <Feature>REST API with Swagger UI at /docs</Feature>
        </Features>

        <Database>
            <Type>SQLite</Type>
            <Location>/root/leetcode_tracker_uv/leetcode.db</Location>
            <Backup>/root/leetcode.db.backup</Backup>
            <Schema>
                <Table name="problems">
                    <Column>id - Primary key</Column>
                    <Column>title - Problem title</Column>
                    <Column>difficulty - Easy/Medium/Hard</Column>
                    <Column>link - LeetCode problem URL</Column>
                    <Column>date_solved - Date when problem was solved</Column>
                    <Column>xp - Experience points (calculated from difficulty)</Column>
                </Table>
            </Schema>
        </Database>
    </LeetCodeTrackerApplication>

    <WebServer>
        <Nginx>
            <Version>1.18.0 (Ubuntu)</Version>
            <Status>Active and running</Status>
            
            <Configuration>
                <MainConfig>/etc/nginx/nginx.conf</MainConfig>
                <SitesAvailable>/etc/nginx/sites-available/</SitesAvailable>
                <SitesEnabled>/etc/nginx/sites-enabled/</SitesEnabled>
                <CurrentSite>/etc/nginx/sites-enabled/novel-cloudtech.ru</CurrentSite>
            </Configuration>

            <VirtualHost>
                <ServerName>novel-cloudtech.com www.novel-cloudtech.com</ServerName>
                <HTTPPort>8888 (redirects to HTTPS:7443)</HTTPPort>
                <HTTPSPort>7443</HTTPSPort>
                <SSL>
                    <Certificate>/etc/letsencrypt/live/novel-cloudtech.com/fullchain.pem</Certificate>
                    <PrivateKey>/etc/letsencrypt/live/novel-cloudtech.com/privkey.pem</PrivateKey>
                    <Protocols>TLSv1.2 TLSv1.3</Protocols>
                </SSL>
                
                <ProxyConfiguration>
                    <Backend>http://127.0.0.1:8000</Backend>
                    <ProxyHeaders>
                        <Header>Host: $host</Header>
                        <Header>X-Real-IP: $remote_addr</Header>
                        <Header>X-Forwarded-For: $proxy_add_x_forwarded_for</Header>
                        <Header>X-Forwarded-Proto: $scheme</Header>
                        <Header>X-Forwarded-Port: $server_port</Header>
                    </ProxyHeaders>
                    <WebSocketSupport>Enabled</WebSocketSupport>
                    <Timeouts>
                        <Connect>60s</Connect>
                        <Send>60s</Send>
                        <Read>60s</Read>
                    </Timeouts>
                </ProxyConfiguration>

                <SecurityHeaders>
                    <Header>X-Frame-Options: DENY</Header>
                    <Header>X-Content-Type-Options: nosniff</Header>
                    <Header>X-XSS-Protection: "1; mode=block"</Header>
                </SecurityHeaders>

                <Logs>
                    <Access>/var/log/nginx/novel-cloudtech.com.access.log</Access>
                    <Error>/var/log/nginx/novel-cloudtech.com.error.log</Error>
                </Logs>
            </VirtualHost>

            <DefaultServers>
                <HTTP_80>Redirects to https://novel-cloudtech.com:7443</HTTP_80>
                <HTTPS_443>Redirects to https://novel-cloudtech.com:7443</HTTPS_443>
            </DefaultServers>

            <Commands>
                <Test>sudo nginx -t</Test>
                <Reload>sudo systemctl reload nginx</Reload>
                <Restart>sudo systemctl restart nginx</Restart>
                <Status>sudo systemctl status nginx</Status>
            </Commands>
        </Nginx>
    </WebServer>

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

    <SystemServices>
        <Service name="leetcode-tracker">
            <Description>LeetCode Tracker FastAPI Application</Description>
            <Status>Active and enabled</Status>
            <ConfigFile>/etc/systemd/system/leetcode-tracker.service</ConfigFile>
            <Commands>
                <Start>sudo systemctl start leetcode-tracker</Start>
                <Stop>sudo systemctl stop leetcode-tracker</Stop>
                <Restart>sudo systemctl restart leetcode-tracker</Restart>
                <Status>sudo systemctl status leetcode-tracker</Status>
                <Enable>sudo systemctl enable leetcode-tracker</Enable>
                <Disable>sudo systemctl disable leetcode-tracker</Disable>
                <Logs>sudo journalctl -u leetcode-tracker -f</Logs>
                <LogsLast50>sudo journalctl -u leetcode-tracker -n 50</LogsLast50>
            </Commands>
        </Service>

        <Service name="docker">
            <Status>Active</Status>
            <AutoStart>Enabled</AutoStart>
            <Commands>
                <Start>sudo systemctl start docker</Start>
                <Stop>sudo systemctl stop docker</Stop>
                <Restart>sudo systemctl restart docker</Restart>
                <Status>sudo systemctl status docker</Status>
            </Commands>
        </Service>

        <Service name="telegram-server-bypass">
            <Status>Active and enabled</Status>
            <Script>/opt/telegram-server-bypass.sh</Script>
            <Commands>
                <Start>sudo systemctl start telegram-server-bypass</Start>
                <Restart>sudo systemctl restart telegram-server-bypass</Restart>
                <Status>sudo systemctl status telegram-server-bypass</Status>
            </Commands>
        </Service>

        <Service name="nginx">
            <Status>Active and enabled</Status>
            <Commands>
                <Start>sudo systemctl start nginx</Start>
                <Stop>sudo systemctl stop nginx</Stop>
                <Reload>sudo systemctl reload nginx</Reload>
                <Restart>sudo systemctl restart nginx</Restart>
                <Status>sudo systemctl status nginx</Status>
            </Commands>
        </Service>
    </SystemServices>

    <FileSystem>
        <ImportantDirectories>
            <Directory path="/root/leetcode_tracker_uv">LeetCode Tracker application root</Directory>
            <Directory path="/var/www/novel-cloudtech.com">Domain-specific web root (not used for app)</Directory>
            <Directory path="/etc/nginx">Nginx configuration</Directory>
            <Directory path="/etc/systemd/system">Systemd service files</Directory>
            <Directory path="/etc/letsencrypt">SSL certificates</Directory>
            <Directory path="/root/.ssh">SSH keys</Directory>
            <Directory path="/opt">Custom scripts (telegram bypass)</Directory>
            <Directory path="/var/log/nginx">Nginx logs</Directory>
        </ImportantDirectories>

        <ImportantFiles>
            <File path="/root/leetcode_tracker_uv/leetcode.db">Main application database</File>
            <File path="/root/leetcode.db.backup">Database backup</File>
            <File path="/root/outline_keys_optimized.txt">All Outline VPN access keys</File>
            <File path="/etc/systemd/system/leetcode-tracker.service">Application systemd service</File>
            <File path="/etc/nginx/sites-enabled/novel-cloudtech.com">Nginx site config with proxy</File>
            <File path="/etc/sysctl.conf">Network optimization settings</File>
            <File path="/etc/iproute2/rt_tables">Routing tables (telegram_direct)</File>
            <File path="/opt/telegram-server-bypass.sh">Telegram bypass autostart script</File>
            <File path="/root/.local/bin/uv">UV package manager binary</File>
        </ImportantFiles>
    </FileSystem>

    <NetworkConfiguration>
        <MainInterface>ens3</MainInterface>
        <DefaultGateway>91.84.104.1</DefaultGateway>
        <PublicIP>91.84.104.36</PublicIP>
        
        <OpenPorts>
            <Port number="22">SSH</Port>
            <Port number="80">HTTP (redirects to 7443)</Port>
            <Port number="443">HTTPS (redirects to 7443)</Port>
            <Port number="7443">HTTPS (main application)</Port>
            <Port number="8000">FastAPI app (localhost only)</Port>
            <Port number="8888">HTTP custom (redirects to 7443)</Port>
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

    <QuickStartGuides>
        <ApplicationDeployment>
            <Title>Deploy LeetCode Tracker Application from Scratch</Title>
            
            <Step number="1">
                <Description>Connect to server</Description>
                <Command>ssh root@v353999.hosted-by-vdsina.com</Command>
                <Alternative>ssh root@91.84.104.36</Alternative>
                <Password>123123123123123123123123123123Aa!</Password>
            </Step>

            <Step number="2">
                <Description>Backup existing database (if exists)</Description>
                <Command>cp /root/leetcode_tracker_uv/leetcode.db /root/leetcode.db.backup</Command>
            </Step>

            <Step number="3">
                <Description>Stop running service (if exists)</Description>
                <Command>systemctl stop leetcode-tracker</Command>
            </Step>

            <Step number="4">
                <Description>Remove old directory and clone fresh code</Description>
                <Commands>
                    <Command>rm -rf /root/leetcode_tracker_uv</Command>
                    <Command>git clone https://github.com/daniil-novel/leetcode-tracker.git /root/leetcode_tracker_uv</Command>
                    <Command>cd /root/leetcode_tracker_uv</Command>
                </Commands>
            </Step>

            <Step number="5">
                <Description>Restore database</Description>
                <Command>cp /root/leetcode.db.backup /root/leetcode_tracker_uv/leetcode.db</Command>
            </Step>

            <Step number="6">
                <Description>Install dependencies with uv</Description>
                <Command>/root/.local/bin/uv sync</Command>
                <Note>This creates .venv and installs all packages</Note>
            </Step>

            <Step number="7">
                <Description>Start and enable service</Description>
                <Commands>
                    <Command>systemctl daemon-reload</Command>
                    <Command>systemctl enable leetcode-tracker</Command>
                    <Command>systemctl start leetcode-tracker</Command>
                </Commands>
            </Step>

            <Step number="8">
                <Description>Verify deployment</Description>
                <Commands>
                    <Command>systemctl status leetcode-tracker</Command>
                    <Command>curl http://127.0.0.1:8000/</Command>
                    <Command>curl -k https://localhost:7443/</Command>
                </Commands>
            </Step>

            <Step number="9">
                <Description>Check logs if needed</Description>
                <Command>journalctl -u leetcode-tracker -f</Command>
            </Step>
        </ApplicationDeployment>

        <UpdateApplicationCode>
            <Title>Update Application to Latest Code</Title>
            
            <Step number="1">
                <Description>Connect to server</Description>
                <Command>ssh root@v353999.hosted-by-vdsina.com</Command>
            </Step>

            <Step number="2">
                <Description>Stop the service</Description>
                <Command>systemctl stop leetcode-tracker</Command>
            </Step>

            <Step number="3">
                <Description>Pull latest code</Description>
                <Commands>
                    <Command>cd /root/leetcode_tracker_uv</Command>
                    <Command>git pull origin main</Command>
                </Commands>
            </Step>

            <Step number="4">
                <Description>Update dependencies</Description>
                <Command>/root/.local/bin/uv sync</Command>
            </Step>

            <Step number="5">
                <Description>Restart service</Description>
                <Command>systemctl start leetcode-tracker</Command>
            </Step>

            <Step number="6">
                <Description>Verify</Description>
                <Command>systemctl status leetcode-tracker</Command>
            </Step>
        </UpdateApplicationCode>

        <LocalDevelopment>
            <Title>Run Application Locally for Development</Title>

            <Step number="1">
                <Description>Clone repository</Description>
                <Command>git clone https://github.com/daniil-novel/leetcode-tracker.git</Command>
            </Step>

            <Step number="2">
                <Description>Install uv (if not installed)</Description>
                <Windows>pip install uv</Windows>
                <Linux_Mac>curl -LsSf https://astral.sh/uv/install.sh | sh</Linux_Mac>
            </Step>

            <Step number="3">
                <Description>Install dependencies</Description>
                <Command>cd leetcode-tracker &amp;&amp; uv sync</Command>
            </Step>

            <Step number="4">
                <Description>Run development server</Description>
                <Command>uv run uvicorn leetcode_tracker.main:app --reload --host 0.0.0.0 --port 8000</Command>
                <Note>Access at http://localhost:8000</Note>
            </Step>

            <Step number="5">
                <Description>Make changes and test</Description>
                <Note>Server auto-reloads on file changes with --reload flag</Note>
            </Step>

            <Step number="6">
                <Description>Push changes to GitHub</Description>
                <Commands>
                    <Command>git add .</Command>
                    <Command>git commit -m "Your commit message"</Command>
                    <Command>git push origin main</Command>
                </Commands>
            </Step>

            <Step number="7">
                <Description>Deploy to server (see UpdateApplicationCode guide)</Description>
            </Step>
        </LocalDevelopment>

        <NginxConfiguration>
            <Title>Update Nginx Configuration</Title>

            <Step number="1">
                <Description>Edit configuration file</Description>
                <Command>nano /etc/nginx/sites-available/novel-cloudtech.com</Command>
                <Note>Or upload via SCP</Note>
            </Step>

            <Step number="2">
                <Description>Test configuration</Description>
                <Command>nginx -t</Command>
            </Step>

            <Step number="3">
                <Description>Reload Nginx</Description>
                <Command>systemctl reload nginx</Command>
            </Step>

            <Step number="4">
                <Description>Verify</Description>
                <Command>systemctl status nginx</Command>
            </Step>
        </NginxConfiguration>

        <DatabaseManagement>
            <Title>Database Backup and Restore</Title>

            <Backup>
                <Description>Create database backup</Description>
                <Command>cp /root/leetcode_tracker_uv/leetcode.db /root/leetcode_backup_$(date +%Y%m%d_%H%M%S).db</Command>
            </Backup>

            <Restore>
                <Description>Restore database from backup</Description>
                <Commands>
                    <Command>systemctl stop leetcode-tracker</Command>
                    <Command>cp /root/leetcode_backup_YYYYMMDD_HHMMSS.db /root/leetcode_tracker_uv/leetcode.db</Command>
                    <Command>systemctl start leetcode-tracker</Command>
                </Commands>
            </Restore>

            <Download>
                <Description>Download database to local machine</Description>
                <Command>scp root@v353999.hosted-by-vdsina.com:/root/leetcode_tracker_uv/leetcode.db ./leetcode.db</Command>
            </Download>

            <Upload>
                <Description>Upload database from local machine</Description>
                <Commands>
                    <Command>scp ./leetcode.db root@v353999.hosted-by-vdsina.com:/root/leetcode_tracker_uv/leetcode.db</Command>
                    <Command>ssh root@v353999.hosted-by-vdsina.com "systemctl restart leetcode-tracker"</Command>
                </Commands>
            </Upload>
        </DatabaseManagement>
    </QuickStartGuides>

    <MaintenanceCommands>
        <SystemUpdates>
            <UpdatePackages>sudo apt update &amp;&amp; sudo apt upgrade -y</UpdatePackages>
            <CleanOldPackages>sudo apt autoremove -y</CleanOldPackages>
            <UpdateUV>pip install --upgrade uv</UpdateUV>
        </SystemUpdates>

        <ApplicationManagement>
            <StartApp>systemctl start leetcode-tracker</StartApp>
            <StopApp>systemctl stop leetcode-tracker</StopApp>
            <RestartApp>systemctl restart leetcode-tracker</RestartApp>
            <StatusApp>systemctl status leetcode-tracker</StatusApp>
            <LogsApp>journalctl -u leetcode-tracker -f</LogsApp>
            <LogsLast100>journalctl -u leetcode-tracker -n 100</LogsLast100>
        </ApplicationManagement>

        <OutlineManagement>
            <ViewAllKeys>curl -k -s "https://127.0.0.1:55515/t4XpSsBVXRc8CQep7Le4Qg/access-keys/" | python3 -m json.tool</ViewAllKeys>
            <CreateKey>curl -k -s -X POST "https://127.0.0.1:55515/t4XpSsBVXRc8CQep7Le4Qg/access-keys/" -H "Content-Type: application/json" -d '{"name": "USERNAME"}'</CreateKey>
            <DeleteKey>curl -k -s -X DELETE "https://127.0.0.1:55515/t4XpSsBVXRc8CQep7Le4Qg/access-keys/KEY_ID"</DeleteKey>
        </OutlineManagement>

        <LogViewing>
            <NginxAccessLog>sudo tail -f /var/log/nginx/access.log</NginxAccessLog>
            <NginxErrorLog>sudo tail -f /var/log/nginx/error.log</NginxErrorLog>
            <AppAccessLog>sudo tail -f /var/log/nginx/novel-cloudtech.com.access.log</AppAccessLog>
            <AppErrorLog>sudo tail -f /var/log/nginx/novel-cloudtech.com.error.log</AppErrorLog>
            <OutlineLogs>sudo docker logs -f shadowbox</OutlineLogs>
            <SystemLog>sudo journalctl -xe</SystemLog>
            <ApplicationLog>sudo journalctl -u leetcode-tracker -f</ApplicationLog>
        </LogViewing>

        <NetworkDiagnostics>
            <CheckRoutes>ip route show</CheckRoutes>
            <CheckTelegramRoutes>ip route get 149.154.160.1</CheckTelegramRoutes>
            <CheckIPTables>sudo iptables -t mangle -L TELEGRAM_BYPASS -n</CheckIPTables>
            <CheckOpenPorts>sudo netstat -tulpn</CheckOpenPorts>
            <CheckListeningPorts>sudo ss -tlnp</CheckListeningPorts>
            <CheckApplicationPort>sudo ss -tlnp | grep :8000</CheckApplicationPort>
            <CheckNginxPorts>sudo ss -tlnp | grep nginx</CheckNginxPorts>
        </NetworkDiagnostics>

        <FileTransfer>
            <UploadFile>scp /local/file root@v353999.hosted-by-vdsina.com:/remote/path</UploadFile>
            <DownloadFile>scp root@v353999.hosted-by-vdsina.com:/remote/file /local/path</DownloadFile>
            <UploadDirectory>scp -r /local/dir root@v353999.hosted-by-vdsina.com:/remote/path</UploadDirectory>
            <DownloadDirectory>scp -r root@v353999.hosted-by-vdsina.com:/remote/dir /local/path</DownloadDirectory>
        </FileTransfer>
    </MaintenanceCommands>

    <TroubleshootingGuide>
        <Issue name="Application not responding">
            <Check1>systemctl status leetcode-tracker</Check1>
            <Check2>journalctl -u leetcode-tracker -n 50</Check2>
            <Check3>curl http://127.0.0.1:8000/</Check3>
            <Check4>ps aux | grep uvicorn</Check4>
            <Solution>systemctl restart leetcode-tracker</Solution>
        </Issue>

        <Issue name="Nginx proxy not working">
            <Check1>systemctl status nginx</Check1>
            <Check2>nginx -t</Check2>
            <Check3>curl -k https://localhost:7443/</Check3>
            <Check4>tail -f /var/log/nginx/novel-cloudtech.com.error.log</Check4>
            <Solution>systemctl reload nginx</Solution>
        </Issue>

        <Issue name="Outline VPN not working">
            <Check1>sudo docker ps | grep shadowbox</Check1>
            <Check2>sudo docker logs shadowbox</Check2>
            <Solution>sudo docker restart shadowbox</Solution>
        </Issue>

        <Issue name="Website not accessible">
            <Check1>systemctl status nginx</Check1>
            <Check2>systemctl status leetcode-tracker</Check2>
            <Check3>ss -tlnp | grep -E ':(8000|7443)'</Check3>
            <Check4>curl -k https://localhost:7443/</Check4>
            <Solution>Check both nginx and leetcode-tracker services, ensure port 7443 is open</Solution>
        </Issue>

        <Issue name="Telegram still using VPN">
            <Check1>ip route get 149.154.160.1</Check1>
            <Check2>systemctl status telegram-server-bypass</Check2>
            <Solution>systemctl restart telegram-server-bypass</Solution>
        </Issue>

        <Issue name="SSL certificate issues">
            <Check1>sudo certbot certificates</Check1>
            <Check2>ls -la /etc/letsencrypt/live/novel-cloudtech.com/</Check2>
            <Solution>sudo certbot renew --force-renewal</Solution>
        </Issue>

        <Issue name="Database errors">
            <Check1>ls -lh /root/leetcode_tracker_uv/leetcode.db</Check1>
            <Check2>sqlite3 /root/leetcode_tracker_uv/leetcode.db "SELECT * FROM problems LIMIT 5;"</Check2>
            <Solution>Restore from backup: cp /root/leetcode.db.backup /root/leetcode_tracker_uv/leetcode.db</Solution>
        </Issue>

        <Issue name="Service won't start">
            <Check1>journalctl -u leetcode-tracker -n 100</Check1>
            <Check2>cd /root/leetcode_tracker_uv &amp;&amp; /root/.local/bin/uv sync</Check2>
            <Check3>Test manually: cd /root/leetcode_tracker_uv &amp;&amp; /root/.local/bin/uv run uvicorn leetcode_tracker.main:app</Check3>
            <Solution>Check logs for specific error, reinstall dependencies if needed</Solution>
        </Issue>

        <Issue name="Port already in use">
            <Check1>sudo ss -tlnp | grep :8000</Check1>
            <Check2>ps aux | grep uvicorn</Check2>
            <Solution>Kill old process: pkill -f uvicorn, then restart service</Solution>
        </Issue>
    </TroubleshootingGuide>

    <BackupRecommendations>
        <Critical>
            <Item priority="highest">/root/leetcode_tracker_uv/leetcode.db - Application database</Item>
            <Item priority="high">/root/outline_keys_optimized.txt - VPN access keys</Item>
            <Item priority="high">/etc/nginx/sites-enabled/novel-cloudtech.com - Nginx configuration</Item>
            <Item priority="high">/etc/systemd/system/leetcode-tracker.service - Application service</Item>
            <Item priority="medium">/root/.ssh/authorized_keys - SSH access</Item>
            <Item priority="medium">/opt/telegram-server-bypass.sh - Custom scripts</Item>
            <Item priority="low">/etc/letsencrypt - SSL certificates (can be regenerated)</Item>
        </Critical>
        
        <BackupCommands>
            <FullBackup>sudo tar -czf /root/backup-$(date +%Y%m%d).tar.gz /root/leetcode_tracker_uv/leetcode.db /etc/nginx/sites-enabled /root/outline_keys_optimized.txt /opt/telegram-server-bypass.sh /etc/systemd/system/leetcode-tracker.service</FullBackup>
            <DatabaseOnly>cp /root/leetcode_tracker_uv/leetcode.db /root/leetcode_backup_$(date +%Y%m%d_%H%M%S).db</DatabaseOnly>
            <DownloadBackup>scp root@v353999.hosted-by-vdsina.com:/root/backup-*.tar.gz ./</DownloadBackup>
        </BackupCommands>

        <AutomatedBackup>
            <Description>Set up daily automated backups with cron</Description>
            <CronJob>0 3 * * * cp /root/leetcode_tracker_uv/leetcode.db /root/backups/leetcode_$(date +\%Y\%m\%d).db</CronJob>
            <Setup>
                <Command>mkdir -p /root/backups</Command>
                <Command>crontab -e</Command>
                <Note>Add the cron job line above</Note>
            </Setup>
        </AutomatedBackup>
    </BackupRecommendations>

    <SecurityNotes>
        <SSH>
            <PasswordAuth>Enabled (use strong password)</PasswordAuth>
            <RootLogin>Permitted (key-based and password)</RootLogin>
            <Port>22 (standard)</Port>
            <Recommendation>Consider using SSH keys only and disabling password auth</Recommendation>
        </SSH>

        <Firewall>
            <Status>Active (iptables)</Status>
            <AllowedPorts>22, 80, 443, 7443, 8888, 55515, UDP for Outline</AllowedPorts>
            <BlockedPorts>8000 (application, localhost only)</BlockedPorts>
        </Firewall>

        <SSL>
            <Protocol>TLS 1.2+</Protocol>
            <AutoRenewal>Enabled via certbot</AutoRenewal>
            <StrongCiphers>Yes</StrongCiphers>
        </SSL>

        <ApplicationSecurity>
            <DatabaseLocation>Not web-accessible</DatabaseLocation>
            <AdminInterface>None (add if needed)</AdminInterface>
            <InputValidation>Handled by FastAPI/Pydantic</InputValidation>
            <CORS>Configure if needed for API access</CORS>
        </ApplicationSecurity>

        <BestPractices>
            <Practice>Regular system updates: apt update &amp;&amp; apt upgrade</Practice>
            <Practice>Monitor logs regularly: journalctl -u leetcode-tracker</Practice>
            <Practice>Regular database backups</Practice>
            <Practice>Keep SSH keys secure</Practice>
            <Practice>Review Nginx access logs for suspicious activity</Practice>
            <Practice>Update application dependencies: /root/.local/bin/uv sync</Practice>
        </BestPractices>
    </SecurityNotes>

    <UsefulCommands>
        <QuickChecks>
            <Command name="Check all services status">
                <Description>Verify all critical services are running</Description>
                <Code>systemctl status nginx leetcode-tracker docker telegram-server-bypass | grep Active</Code>
            </Command>
            
            <Command name="Check application health">
                <Description>Quick health check of the application</Description>
                <Code>curl -s http://127.0.0.1:8000/ | head -5 &amp;&amp; echo "Application is responding"</Code>
            </Command>

            <Command name="Check disk usage">
                <Description>Monitor disk space</Description>
                <Code>df -h</Code>
            </Command>

            <Command name="Check memory usage">
                <Description>Monitor memory usage</Description>
                <Code>free -h</Code>
            </Command>

            <Command name="Check running processes">
                <Description>View resource-intensive processes</Description>
                <Code>top -bn1 | head -20</Code>
            </Command>

            <Command name="View application logs live">
                <Description>Monitor application logs in real-time</Description>
                <Code>journalctl -u leetcode-tracker -f</Code>
            </Command>

            <Command name="Test HTTPS endpoint">
                <Description>Verify HTTPS is working</Description>
                <Code>curl -I -k https://localhost:7443/</Code>
            </Command>
        </QuickChecks>

        <EmergencyCommands>
            <Command name="Restart all services">
                <Description>Restart all critical services</Description>
                <Code>systemctl restart nginx leetcode-tracker</Code>
            </Command>

            <Command name="View recent errors">
                <Description>Check recent system errors</Description>
                <Code>journalctl -p err -n 50</Code>
            </Command>

            <Command name="Kill stuck processes">
                <Description>Kill all uvicorn processes if stuck</Description>
                <Code>pkill -9 -f uvicorn</Code>
            </Command>
        </EmergencyCommands>
    </UsefulCommands>

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

        <Issue>
            <Problem>FastAPI application needs custom port for HTTPS</Problem>
            <Cause>Standard ports 80/443 redirect to custom port</Cause>
            <Solution>Application accessible on port 7443 via Nginx reverse proxy</Solution>
            <Status>Working as designed</Status>
        </Issue>
    </KnownIssuesAndSolutions>

    <FutureConsiderations>
        <Item priority="high">Add user authentication to LeetCode Tracker</Item>
        <Item priority="high">Implement automated database backups with retention policy</Item>
        <Item priority="medium">Consider PostgreSQL migration for better performance</Item>
        <Item priority="medium">Add monitoring/alerting (e.g., Prometheus, Grafana)</Item>
        <Item priority="medium">Implement CI/CD pipeline for automatic deployments</Item>
        <Item priority="low">Add API rate limiting</Item>
        <Item priority="low">Implement caching layer (Redis)</Item>
        <Item priority="low">Add comprehensive logging and analytics</Item>
        <Item priority="low">Consider containerizing the application with Docker</Item>
    </FutureConsiderations>

    <ContactInformation>
        <Server>
            <Provider>VDSina.ru</Provider>
            <SupportURL>https://vdsina.ru/support</SupportURL>
        </Server>
        
        <Application>
            <Repository>https://github.com/daniil-novel/leetcode-tracker</Repository>
            <Developer>Daniil Novel</Developer>
        </Application>
    </ContactInformation>

    <VersionHistory>
        <Version number="2.1" date="2025-11-25">
            <Changes>
                <Change>Fixed static file path in base.html from Flask `url_for` to FastAPI compliant `/static/`</Change>
                <Change>Updated database schema with `time_spent` column (required recreation of leetcode.db on server)</Change>
                <Change>Added new features: time spent tracking, CSV import functionality, and detailed month statistics with calendar view</Change>
                <Change>Updated Nginx configuration details</Change>
                <Change>Minor documentation improvements and updates to reflect latest code</Change>
            </Changes>
        </Version>
        
        <Version number="2.0" date="2025-11-25">
            <Changes>
                <Change>Added complete LeetCode Tracker application deployment information</Change>
                <Change>Added systemd service configuration details</Change>
                <Change>Expanded Nginx reverse proxy configuration</Change>
                <Change>Added comprehensive step-by-step deployment guides</Change>
                <Change>Included local development workflow</Change>
                <Change>Added troubleshooting section for common issues</Change>
                <Change>Documented all service management commands</Change>
                <Change>Added database backup and restore procedures</Change>
                <Change>Included security best practices</Change>
                <Change>Added useful commands and emergency procedures</Change>
            </Changes>
        </Version>
        
        <Version number="1.0" date="2024-09-19">
            <Changes>
                <Change>Initial server setup with Outline VPN</Change>
                <Change>Nginx web server configuration</Change>
                <Change>SSL certificates setup</Change>
                <Change>Telegram bypass optimization</Change>
            </Changes>
        </Version>
    </VersionHistory>
</ServerKnowledgeBase>
