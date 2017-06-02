Rem setup script

Const WINDOW_HANDLE = 0 
Const OPTIONS = 0
Const strDepPath = "C:\scripts"
Dim fso
Set fso = CreateObject("Scripting.FileSystemObject")


Rem 1.设置python解释器路径
Set objShell = CreateObject("Shell.Application") 
Set objFolder = objShell.BrowseForFolder _ 
(WINDOW_HANDLE, "Python解释器路径:", OPTIONS, "")
If objFolder Is Nothing Then
	MsgBox "路径无效, 脚本退出"
	Wscript.Quit 
End If 
strPythonPath = objFolder.Self.Path : 'python解释器路径，后面无\
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

MsgBox "安装完成！"

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