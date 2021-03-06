Rem setup script

Rem --------------------------------函数定义 begin
Rem 获取Python3x的Path路径
Function GetPy3xPath()
	Set WshShell= CreateObject("WScript.Shell")
	pathStr = WshShell.ExpandEnvironmentStrings("%path%")
	pattern = ";?([C-Z]:\\[^:;]+[Pp]ython3[0-9][/\\])[;$]"

	Dim re, match, matches
	Set re = New RegExp
	re.Pattern = pattern
	re.IgnoreCase = True
	Set matches = re.Execute(pathStr)
	
	retStr = ""
	If re.Test(pathStr) Then
		retStr = matches(0).SubMatches(0)
	End If
	GetPy3xPath = retStr
End Function

Rem 拷贝文件夹
Function CpFolder(fso, source, destination, overwrite)
    Dim s, d, f, l
    Set s = fso.GetFolder(source)

    If Not fso.FolderExists(destination) Then
        fso.CreateFolder destination
    End If
    Set d = fso.GetFolder(destination)

    For Each f In s.Files
        l = d.Path & "\" & f.Name
        If Not fso.FileExists(l) Or overwrite Then
            If fso.FileExists(l) Then
                fso.DeleteFile l, True
            End If
            f.Copy l, True
        End If
    Next

    For Each f In s.SubFolders
        call CpFolder(fso, f.Path, d.Path & "\" & f.Name, overwrite)
    Next

End Function

Rem --------------------------------函数定义 end


Rem --------------------------------安装脚本：
DebugVersion = False
interpreter = "\pythonw.exe"
If DebugVersion Then
	interpreter = "\python.exe"
End If

Const WINDOW_HANDLE = 0 
Const OPTIONS = 0
strDepPath = "" :'安装路径
Dim fso
Set fso = CreateObject("Scripting.FileSystemObject")

Rem 1.设置python解释器路径
strPythonPath = GetPy3xPath()
If strPythonPath = "" Then
	Set objShell = CreateObject("Shell.Application") 
	Set objFolder = objShell.BrowseForFolder _ 
	(WINDOW_HANDLE, "Python解释器路径:", OPTIONS, "")
	If objFolder Is Nothing Then
		MsgBox "路径无效, 脚本退出", vbInformation, "错误"
		Wscript.Quit 
	End If
    strPythonPath = objFolder.Self.Path
End If
Rem MsgBox strPythonPath & interpreter, vbInformation, "strPythonPath & interpreter"
If Not fso.FileExists(strPythonPath & interpreter) Then
	MsgBox "未找到 pythonw.exe, 脚本退出", vbInformation, "错误"
	Wscript.Quit
End If

Rem 2.设置安装路径
Set objShell = CreateObject("Shell.Application") 
Set objFolder = objShell.BrowseForFolder _ 
(WINDOW_HANDLE, "安装路径:", 0, "")
If objFolder Is Nothing Then
	MsgBox "路径无效, 脚本退出", vbInformation, "错误"
	Wscript.Quit 
End If
strDepPath = objFolder.Self.Path :'安装路径，后面无\
If Not fso.FolderExists(strDepPath) Then
	fso.CreateFolder strDepPath
End If

Rem 3.设置保存路径
Set objShell = CreateObject("Shell.Application") 
Set objFolder = objShell.BrowseForFolder _ 
(WINDOW_HANDLE, "墙纸保存路径:", OPTIONS, "")
If objFolder Is Nothing Then
	MsgBox "路径无效, 脚本退出", vbInformation, "错误"
	Wscript.Quit 
End If
strSavePath = objFolder.Self.Path :'保存路径，后面无\
If Not fso.FolderExists(strSavePath) Then
	fso.CreateFolder strSavePath
End If

Rem 4.部署脚本至 C:\scripts\
currentPath = createobject("Scripting.FileSystemObject").GetFile(Wscript.ScriptFullName).ParentFolder.Path
call CpFolder(fso, currentPath, strDepPath, True)

Rem 5.创建开机启动
Set WshShell = WScript.CreateObject("WScript.Shell")
strStartup = WshShell.SpecialFolders("Startup")
set oShellLink = WshShell.CreateShortcut(strStartup & "\dlbingwallpaper.lnk")
oShellLink.TargetPath = strPythonPath & interpreter
oShellLink.Arguments = strDepPath & "\dlbingwallpaper.py " & strSavePath
oShellLink.WorkingDirectory = strDepPath
oShellLink.WindowStyle = 1 :'1 默认窗口 3 最大化 7 最小化
oShellLink.Description = ""
oShellLink.Save

Rem 6.给浏览器创建桌面快捷方式
strStartup = WshShell.SpecialFolders("Desktop")
set oShellLink = WshShell.CreateShortcut(strStartup & "\wallpaperbrowser.lnk")
oShellLink.TargetPath = strPythonPath & interpreter
oShellLink.Arguments = strDepPath & "\wallpaperbrowser.py " & strSavePath & " " & strDepPath
oShellLink.WorkingDirectory = strDepPath
oShellLink.WindowStyle = 1 :'1 默认窗口 3 最大化 7 最小化
oShellLink.Description = ""
oShellLink.Save

MsgBox "安装完成！", vbInformation, "setup"