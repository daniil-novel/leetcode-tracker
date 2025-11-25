# 🖥️ Полное руководство по работе с сервером

## 📋 Общая информация о сервере

```xml
<server_info>
  <host>
    <primary>v353999.hosted-by-vdsina.com</primary>
    <ip>91.84.104.36</ip>
  </host>
  <credentials>
    <user>root</user>
    <password>123123123123123123123123123123Aa!</password>
  </credentials>
  <connection>
    <method>SSH</method>
    <port>22</port>
    <tool>PuTTY (для Windows) или ssh (для Linux/Mac)</tool>
  </connection>
</server_info>
```

## 🗂️ Структура проекта

```xml
<project_structure>
  <local_path>e:\leetcode_tracker_uv</local_path>
  <server_path>/root/leetcode_tracker_uv</server_path>
  
  <main_files>
    <python_files>
      <file>leetcode_tracker/main.py</file>         <!-- Главный файл приложения -->
      <file>leetcode_tracker/auth.py</file>         <!-- Авторизация -->
      <file>leetcode_tracker/models.py</file>       <!-- Модели БД -->
      <file>leetcode_tracker/schemas.py</file>      <!-- Pydantic схемы -->
      <file>leetcode_tracker/ranks.py</file>        <!-- Система рангов -->
      <file>leetcode_tracker/database.py</file>     <!-- Настройки БД -->
    </python_files>
    
    <templates>
      <file>leetcode_tracker/templates/base.html</file>
      <file>leetcode_tracker/templates/index.html</file>
      <file>leetcode_tracker/templates/login.html</file>
    </templates>
    
    <static>
      <file>leetcode_tracker/static/main.css</file>
    </static>
    
    <config>
      <file>pyproject.toml</file>                   <!-- Зависимости проекта -->
      <file>.env</file>                             <!-- Переменные окружения (не в git) -->
    </config>
  </main_files>
</project_structure>
```

## 🔌 Подключение к серверу

```xml
<connection_steps>
  <method name="SSH через командную строку">
    <step number="1">
      <command>ssh root@v353999.hosted-by-vdsina.com</command>
      <description>Подключиться к серверу</description>
      <password_prompt>Ввести пароль: 123123123123123123123123123123Aa!</password_prompt>
    </step>
  </method>
  
  <method name="PuTTY (Windows)">
    <step number="1">Открыть PuTTY</step>
    <step number="2">Host Name: v353999.hosted-by-vdsina.com</step>
    <step number="3">Port: 22</step>
    <step number="4">Connection type: SSH</step>
    <step number="5">Click: Open</step>
    <step number="6">Login as: root</step>
    <step number="7">Password: 123123123123123123123123123123Aa!</step>
  </method>
</connection_steps>
```

## 🚀 Запуск приложения на сервере

```xml
<server_operations>
  <environment>
    <python_version>3.10</python_version>
    <package_manager>uv</package_manager>
    <uv_path>/root/.local/bin/uv</uv_path>
    <project_dir>/root/leetcode_tracker_uv</project_dir>
    <venv_path>/root/leetcode_tracker_uv/.venv</venv_path>
  </environment>
  
  <startup_sequence>
    <step number="1">
      <name>Перейти в директорию проекта</name>
      <command>cd /root/leetcode_tracker_uv</command>
    </step>
    
    <step number="2">
      <name>Убить старый процесс (если запущен)</name>
      <command>pkill -f uvicorn</command>
      <note>Игнорировать ошибку если процесс не найден</note>
    </step>
    
    <step number="3">
      <name>Запустить приложение в фоне</name>
      <command>nohup /root/.local/bin/uv run uvicorn leetcode_tracker.main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &</command>
      <description>
        - nohup: запуск в фоне (не прерывается при отключении SSH)
        - /root/.local/bin/uv: полный путь к uv
        - run uvicorn: запустить uvicorn через uv
        - --host 0.0.0.0: доступ со всех IP
        - --port 8000: порт приложения
        - > app.log 2>&1: перенаправить вывод в app.log
        - &: запуск в фоне
      </description>
    </step>
    
    <step number="4">
      <name>Проверить что процесс запустился</name>
      <command>ps aux | grep uvicorn | grep -v grep</command>
      <expected_output>
        root      XXXXX  X.X  X.X XXXXXX XXXXX ?        Sl   HH:MM   0:XX /root/.local/bin/uv run uvicorn...
      </expected_output>
    </step>
    
    <step number="5">
      <name>Проверить логи</name>
      <command>tail -20 app.log</command>
      <expected_output>
        INFO:     Started server process [XXXXX]
        INFO:     Waiting for application startup.
        INFO:     Application startup complete.
        INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
      </expected_output>
    </step>
  </startup_sequence>
  
  <quick_restart>
    <name>Быстрый перезапуск одной командой</name>
    <command>cd /root/leetcode_tracker_uv && pkill -f uvicorn; nohup /root/.local/bin/uv run uvicorn leetcode_tracker.main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 & sleep 3 && tail -10 app.log</command>
  </quick_restart>
</server_operations>
```

## 📤 Загрузка изменений на сервер

```xml
<deployment>
  <method name="SCP (рекомендуется для отдельных файлов)">
    <python_files>
      <command>scp leetcode_tracker/main.py root@v353999.hosted-by-vdsina.com:/root/leetcode_tracker_uv/leetcode_tracker/</command>
      <command>scp leetcode_tracker/auth.py root@v353999.hosted-by-vdsina.com:/root/leetcode_tracker_uv/leetcode_tracker/</command>
      <command>scp leetcode_tracker/models.py root@v353999.hosted-by-vdsina.com:/root/leetcode_tracker_uv/leetcode_tracker/</command>
      <command>scp leetcode_tracker/schemas.py root@v353999.hosted-by-vdsina.com:/root/leetcode_tracker_uv/leetcode_tracker/</command>
      <command>scp leetcode_tracker/ranks.py root@v353999.hosted-by-vdsina.com:/root/leetcode_tracker_uv/leetcode_tracker/</command>
    </python_files>
    
    <templates>
      <command>scp leetcode_tracker/templates/login.html leetcode_tracker/templates/base.html leetcode_tracker/templates/index.html root@v353999.hosted-by-vdsina.com:/root/leetcode_tracker_uv/leetcode_tracker/templates/</command>
    </templates>
    
    <static>
      <command>scp leetcode_tracker/static/main.css root@v353999.hosted-by-vdsina.com:/root/leetcode_tracker_uv/leetcode_tracker/static/</command>
    </static>
  </method>
  
  <method name="SSH с выполнением команд">
    <single_file>
      <description>Загрузить один файл и перезапустить</description>
      <command>scp leetcode_tracker/main.py root@v353999.hosted-by-vdsina.com:/root/leetcode_tracker_uv/leetcode_tracker/ && ssh root@v353999.hosted-by-vdsina.com "cd /root/leetcode_tracker_uv && pkill -f uvicorn && nohup /root/.local/bin/uv run uvicorn leetcode_tracker.main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &"</command>
    </single_file>
  </method>
  
  <typical_workflow>
    <step number="1">
      <name>Внести изменения локально</name>
      <description>Отредактировать файлы на локальной машине</description>
    </step>
    
    <step number="2">
      <name>Загрузить измененные файлы</name>
      <example>scp leetcode_tracker/main.py root@v353999.hosted-by-vdsina.com:/root/leetcode_tracker_uv/leetcode_tracker/</example>
    </step>
    
    <step number="3">
      <name>Перезапустить приложение</name>
      <command>ssh root@v353999.hosted-by-vdsina.com "cd /root/leetcode_tracker_uv && pkill -f uvicorn && nohup /root/.local/bin/uv run uvicorn leetcode_tracker.main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &"</command>
    </step>
    
    <step number="4">
      <name>Проверить логи</name>
      <command>ssh root@v353999.hosted-by-vdsina.com "tail -20 /root/leetcode_tracker_uv/app.log"</command>
    </step>
  </typical_workflow>
</deployment>
```

## 🔍 Диагностика и проверка

```xml
<diagnostics>
  <check_process>
    <name>Проверить запущенные процессы</name>
    <command>ssh root@v353999.hosted-by-vdsina.com "ps aux | grep uvicorn | grep -v grep"</command>
    <interpretation>
      <running>Если есть вывод - приложение работает</running>
      <not_running>Если пусто - приложение не запущено</not_running>
    </interpretation>
  </check_process>
  
  <check_logs>
    <name>Просмотр логов</name>
    <last_lines>
      <command>ssh root@v353999.hosted-by-vdsina.com "tail -20 /root/leetcode_tracker_uv/app.log"</command>
    </last_lines>
    <full_log>
      <command>ssh root@v353999.hosted-by-vdsina.com "cat /root/leetcode_tracker_uv/app.log"</command>
    </full_log>
    <live_monitoring>
      <command>ssh root@v353999.hosted-by-vdsina.com "tail -f /root/leetcode_tracker_uv/app.log"</command>
      <note>CTRL+C для выхода</note>
    </live_monitoring>
  </check_logs>
  
  <check_http>
    <name>Проверка HTTP доступности</name>
    <local_check>
      <command>ssh root@v353999.hosted-by-vdsina.com "curl -s http://localhost:8000 | head -20"</command>
      <expected>HTML код страницы</expected>
    </local_check>
    <external_check>
      <url>http://v353999.hosted-by-vdsina.com:8000</url>
      <url_alt>http://91.84.104.36:8000</url_alt>
      <description>Открыть в браузере</description>
    </external_check>
  </check_http>
  
  <check_database>
    <name>Проверка базы данных</name>
    <command>ssh root@v353999.hosted-by-vdsina.com "ls -lh /root/leetcode_tracker_uv/leetcode_tracker.db"</command>
    <reset_db>
      <command>ssh root@v353999.hosted-by-vdsina.com "cd /root/leetcode_tracker_uv && rm -f leetcode_tracker.db"</command>
      <note>БД будет автоматически пересоздана при следующем запуске</note>
    </reset_db>
  </check_database>
</diagnostics>
```

## 🛠️ Управление зависимостями

```xml
<dependencies>
  <install_new_package>
    <step number="1">
      <name>Добавить пакет через uv</name>
      <command>ssh root@v353999.hosted-by-vdsina.com "cd /root/leetcode_tracker_uv && /root/.local/bin/uv add PACKAGE_NAME"</command>
      <examples>
        <example>uv add httpx</example>
        <example>uv add python-jose[cryptography]</example>
        <example>uv add email-validator</example>
      </examples>
    </step>
  </install_new_package>
  
  <sync_dependencies>
    <name>Синхронизировать все зависимости</name>
    <command>ssh root@v353999.hosted-by-vdsina.com "cd /root/leetcode_tracker_uv && /root/.local/bin/uv sync"</command>
    <when_to_use>
      <case>После загрузки нового pyproject.toml</case>
      <case>При проблемах с зависимостями</case>
    </when_to_use>
  </sync_dependencies>
  
  <current_packages>
    <critical_packages>
      <package>fastapi</package>
      <package>uvicorn</package>
      <package>sqlalchemy</package>
      <package>pydantic</package>
      <package>python-jose[cryptography]</package>
      <package>passlib[bcrypt]</package>
      <package>httpx</package>
      <package>authlib</package>
      <package>itsdangerous</package>
      <package>email-validator</package>
    </critical_packages>
  </current_packages>
</dependencies>
```

## ❗ Типичные проблемы и решения

```xml
<troubleshooting>
  <problem name="Приложение не запускается">
    <symptom>После команды запуска нет процесса</symptom>
    <solutions>
      <solution number="1">
        <name>Проверить логи на ошибки</name>
        <command>ssh root@v353999.hosted-by-vdsina.com "cat /root/leetcode_tracker_uv/app.log"</command>
      </solution>
      <solution number="2">
        <name>Попробовать запустить без nohup</name>
        <command>ssh root@v353999.hosted-by-vdsina.com "cd /root/leetcode_tracker_uv && /root/.local/bin/uv run uvicorn leetcode_tracker.main:app --host 0.0.0.0 --port 8000"</command>
        <note>Увидите ошибки в реальном времени</note>
      </solution>
      <solution number="3">
        <name>Проверить отсутствие импортов</name>
        <common_errors>
          <error>ModuleNotFoundError: No module named 'XXXXX'</error>
          <fix>Установить пакет: uv add XXXXX</fix>
        </common_errors>
      </solution>
    </solutions>
  </problem>
  
  <problem name="Порт 8000 занят">
    <symptom>Address already in use</symptom>
    <solutions>
      <solution number="1">
        <name>Найти и убить процесс</name>
        <commands>
          <command>ssh root@v353999.hosted-by-vdsina.com "lsof -i :8000"</command>
          <command>ssh root@v353999.hosted-by-vdsina.com "pkill -f uvicorn"</command>
        </commands>
      </solution>
    </solutions>
  </problem>
  
  <problem name="401 Unauthorized при API запросах">
    <symptom>API возвращает 401</symptom>
    <solutions>
      <solution number="1">
        <name>Проверить токен в localStorage</name>
        <description>Токен должен храниться в localStorage браузера</description>
      </solution>
      <solution number="2">
        <name>Проверить SECRET_KEY в .env</name>
        <location>/root/leetcode_tracker_uv/.env</location>
      </solution>
    </solutions>
  </problem>
  
  <problem name="База данных со старой схемой">
    <symptom>Ошибки при работе с БД, missing columns</symptom>
    <solutions>
      <solution number="1">
        <name>Удалить старую БД</name>
        <command>ssh root@v353999.hosted-by-vdsina.com "cd /root/leetcode_tracker_uv && rm -f leetcode_tracker.db"</command>
        <note>БД будет пересоздана автоматически</note>
      </solution>
    </solutions>
  </problem>
</troubleshooting>
```

## 📝 Примеры полных сценариев

```xml
<complete_scenarios>
  <scenario name="Обновление кода на сервере">
    <description>Типичный сценарий обновления приложения</description>
    <steps>
      <step number="1">
        <action>Внести изменения локально</action>
        <files>main.py, auth.py</files>
      </step>
      
      <step number="2">
        <action>Загрузить файлы на сервер</action>
        <command>scp leetcode_tracker/main.py leetcode_tracker/auth.py root@v353999.hosted-by-vdsina.com:/root/leetcode_tracker_uv/leetcode_tracker/</command>
      </step>
      
      <step number="3">
        <action>Перезапустить приложение</action>
        <command>ssh root@v353999.hosted-by-vdsina.com "cd /root/leetcode_tracker_uv && pkill -f uvicorn && nohup /root/.local/bin/uv run uvicorn leetcode_tracker.main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &"</command>
      </step>
      
      <step number="4">
        <action>Проверить запуск</action>
        <command>ssh root@v353999.hosted-by-vdsina.com "sleep 3 && tail -20 /root/leetcode_tracker_uv/app.log"</command>
      </step>
      
      <step number="5">
        <action>Проверить в браузере</action>
        <url>http://v353999.hosted-by-vdsina.com:8000</url>
      </step>
    </steps>
  </scenario>
  
  <scenario name="Добавление новой зависимости">
    <description>Добавление нового Python пакета</description>
    <steps>
      <step number="1">
        <action>Добавить зависимость через SSH</action>
        <command>ssh root@v353999.hosted-by-vdsina.com "cd /root/leetcode_tracker_uv && /root/.local/bin/uv add PACKAGE_NAME"</command>
      </step>
      
      <step number="2">
        <action>Обновить код для использования пакета</action>
        <description>Внести изменения в Python файлы</description>
      </step>
      
      <step number="3">
        <action>Загрузить измененные файлы</action>
        <command>scp измененные_файлы root@v353999.hosted-by-vdsina.com:/root/leetcode_tracker_uv/leetcode_tracker/</command>
      </step>
      
      <step number="4">
        <action>Перезапустить</action>
        <command>ssh root@v353999.hosted-by-vdsina.com "cd /root/leetcode_tracker_uv && pkill -f uvicorn && nohup /root/.local/bin/uv run uvicorn leetcode_tracker.main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &"</command>
      </step>
    </steps>
  </scenario>
  
  <scenario name="Полная диагностика проблем">
    <description>Когда что-то не работает</description>
    <steps>
      <step number="1">
        <action>Проверить процессы</action>
        <command>ssh root@v353999.hosted-by-vdsina.com "ps aux | grep uvicorn"</command>
      </step>
      
      <step number="2">
        <action>Посмотреть логи</action>
        <command>ssh root@v353999.hosted-by-vdsina.com "tail -50 /root/leetcode_tracker_uv/app.log"</command>
      </step>
      
      <step number="3">
        <action>Проверить localhost</action>
        <command>ssh root@v353999.hosted-by-vdsina.com "curl -s http://localhost:8000 | head -20"</command>
      </step>
      
      <step number="4">
        <action>Проверить файлы проекта</action>
        <command>ssh root@v353999.hosted-by-vdsina.com "ls -la /root/leetcode_tracker_uv/leetcode_tracker/"</command>
      </step>
      
      <step number="5">
        <action>Попробовать запустить вручную без фона</action>
        <command>ssh root@v353999.hosted-by-vdsina.com "cd /root/leetcode_tracker_uv && /root/.local/bin/uv run uvicorn leetcode_tracker.main:app --host 0.0.0.0 --port 8000"</command>
      </step>
    </steps>
  </scenario>
</complete_scenarios>
```

## 🔐 Безопасность и переменные окружения

```xml
<security>
  <env_file>
    <location>/root/leetcode_tracker_uv/.env</location>
    <variables>
      <variable>
        <name>SECRET_KEY</name>
        <description>Ключ для JWT токенов</description>
        <current>your-secret-key-change-in-production</current>
        <recommendation>Сменить на случайную строку в продакшене</recommendation>
      </variable>
      
      <variable>
        <name>GITHUB_CLIENT_ID</name>
        <description>ID приложения GitHub OAuth (если используется)</description>
      </variable>
      
      <variable>
        <name>GITHUB_CLIENT_SECRET</name>
        <description>Секрет приложения GitHub OAuth (если используется)</description>
      </variable>
    </variables>
    
    <create_env>
      <command>ssh root@v353999.hosted-by-vdsina.com "cat > /root/leetcode_tracker_uv/.env << 'EOF'
SECRET_KEY=your-random-secret-key-here
EOF"</command>
    </create_env>
  </env_file>
</security>
```

## 📊 Мониторинг и логирование

```xml
<monitoring>
  <log_files>
    <main_log>
      <path>/root/leetcode_tracker_uv/app.log</path>
      <description>Основной лог приложения</description>
      <commands>
        <view_last>tail -50 app.log</view_last>
        <view_all>cat app.log</view_all>
        <clear>echo "" > app.log</clear>
        <follow>tail -f app.log</follow>
      </commands>
    </main_log>
  </log_files>
  
  <access_urls>
    <main>http://v353999.hosted-by-vdsina.com:8000</main>
    <login>http://v353999.hosted-by-vdsina.com:8000/login</login>
    <api>http://v353999.hosted-by-vdsina.com:8000/api/tasks</api>
  </access_urls>
</monitoring>
```

## 💡 Полезные команды для копирования

```xml
<quick_commands>
  <restart_service>
    <description>Быстрый перезапуск</description>
    <command>ssh root@v353999.hosted-by-vdsina.com "cd /root/leetcode_tracker_uv && pkill -f uvicorn; nohup /root/.local/bin/uv run uvicorn leetcode_tracker.main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 & sleep 3 && tail -10 app.log"</command>
  </restart_service>
  
  <upload_all_python>
    <description>Загрузить все Python файлы</description>
    <command>scp leetcode_tracker/*.py root@v353999.hosted-by-vdsina.com:/root/leetcode_tracker_uv/leetcode_tracker/</command>
  </upload_all_python>
  
  <upload_all_templates>
    <description>Загрузить все шаблоны</description>
    <command>scp leetcode_tracker/templates/*.html root@v353999.hosted-by-vdsina.com:/root/leetcode_tracker_uv/leetcode_tracker/templates/</command>
  </upload_all_templates>
  
  <full_status>
    <description>Полная проверка статуса</description>
    <command>ssh root@v353999.hosted-by-vdsina.com "ps aux | grep uvicorn | grep -v grep && echo '---' && tail -10 /root/leetcode_tracker_uv/app.log"</command>
  </full_status>
</quick_commands>
```

---

## 📞 Контакты и справка

- **Хост сервера:** v353999.hosted-by-vdsina.com
- **IP:** 91.84.104.36
- **Порт приложения:** 8000
- **Доступ:** http://v353999.hosted-by-vdsina.com:8000

**Важно:** Эта инструкция содержит учетные данные и должна храниться в безопасном месте!
