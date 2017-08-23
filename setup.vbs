Rem setup script

Rem --------------------------------函数定义 begin
Rem 获取Python3x的Path路径
Function GetPy3xPath()
	Set WshShell= CreateObject("WScript.Shell")
	pathStr = WshShell.ExpandEnvironmentStrings("%path%")
	pattern = ";(.+\\[Pp]ython3[0-9][/\\]);"

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
Const WINDOW_HANDLE = 0 
Const OPTIONS = 0
Const strDepPath = "C:\scripts"
Dim fso
Set fso = CreateObject("Scripting.FileSystemObject")

Rem 1.设置python解释器路径
strPythonPath = GetPy3xPath()
MsgBox strPythonPath
If strPythonPath = "" Then
	MsgBox "in if"
	Set objShell = CreateObject("Shell.Application") 
	Set objFolder = objShell.BrowseForFolder _ 
	(WINDOW_HANDLE, "Python解释器路径:", OPTIONS, "")
	If objFolder Is Nothing Then
		MsgBox "路径无效, 脚本退出"
		Wscript.Quit 
	End If
	strPythonPath = objFolder.Self.Path
End If
MsgBox strPythonPath
If Not fso.FileExists(strPythonPath & "\python.exe") Then
	MsgBox "未找到 python.exe, 脚本退出"
	Wscript.Quit
End If

Rem 2.设置保存路径
Set objShell = CreateObject("Shell.Application") 
Set objFolder = objShell.BrowseForFolder _ 
(WINDOW_HANDLE, "墙纸保存路径:", OPTIONS, "")
If objFolder Is Nothing Then
	MsgBox "路径无效, 脚本退出"
	Wscript.Quit 
End If
strSavePath = objFolder.Self.Path : '保存路径，后面无\
If Not fso.FolderExists(strSavePath) Then
	fso.CreateFolder strSavePath
End If

Rem 3.部署脚本至 C:\scripts\
currentPath = createobject("Scripting.FileSystemObject").GetFile(Wscript.ScriptFullName).ParentFolder.Path
call CpFolder(fso, currentPath, strDepPath, True)

Rem 4.创建开机启动
Set WshShell = WScript.CreateObject("WScript.Shell")
strStartup = WshShell.SpecialFolders("Startup")
set oShellLink = WshShell.CreateShortcut(strStartup & "\dlbingwallpaper.lnk")
oShellLink.TargetPath = strPythonPath & "\python.exe"
oShellLink.Arguments = strDepPath & "\dlbingwallpaper.py " & strSavePath
oShellLink.WorkingDirectory = strDepPath
oShellLink.WindowStyle = 1 :'1 默认窗口 3 最大化 7 最小化
oShellLink.Description = ""
oShellLink.Save

Rem 5.给浏览器创建桌面快捷方式
strStartup = WshShell.SpecialFolders("Desktop")
set oShellLink = WshShell.CreateShortcut(strStartup & "\wallpaperbrowser.lnk")
oShellLink.TargetPath = strPythonPath & "\python.exe"
oShellLink.Arguments = strDepPath & "\wallpaperbrowser.py " & strSavePath & " " & strDepPath
oShellLink.WorkingDirectory = strDepPath
oShellLink.WindowStyle = 1 :'1 默认窗口 3 最大化 7 最小化
oShellLink.Description = ""
oShellLink.Save

MsgBox "安装完成！"