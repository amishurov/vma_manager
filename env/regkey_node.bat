reg add HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Selenium\Parameters /v Application /d "java -Xmx512m -jar \"C:\selenium\selenium.jar\" -Dwebdriver.chrome.driver=\"C:\chromedriver.exe\" -role node -nodeConfig \"C:\selenium\node.json\"" /f
echo "OK"
