@ECHO OFF
set /a x=1
adb devices

:while
IF EXIST "chapter%x%.xml" (
	set /a x+=1
	GOTO while
)
adb shell uiautomator dump && adb pull /sdcard/window_dump.xml chapter%x%.xml