reg add HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Selenium\Parameters /v Application /d "\"java.exe\" -jar \"C:\selenium\selenium.jar\"  -Dwebdriver.chrome.driver=\"C:\chromedriver.exe\"" /f
echo "OK"
