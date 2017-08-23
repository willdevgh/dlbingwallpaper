Rem setup script

Rem --------------------------------�������� begin
Rem ��ȡPython3x��Path·��
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

Rem �����ļ���
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

Rem --------------------------------�������� end


Rem --------------------------------��װ�ű���
Const WINDOW_HANDLE = 0 
Const OPTIONS = 0
Const strDepPath = "C:\scripts"
Dim fso
Set fso = CreateObject("Scripting.FileSystemObject")

Rem 1.����python������·��
strPythonPath = GetPy3xPath()
MsgBox strPythonPath
If strPythonPath = "" Then
	MsgBox "in if"
	Set objShell = CreateObject("Shell.Application") 
	Set objFolder = objShell.BrowseForFolder _ 
	(WINDOW_HANDLE, "Python������·��:", OPTIONS, "")
	If objFolder Is Nothing Then
		MsgBox "·����Ч, �ű��˳�"
		Wscript.Quit 
	End If
	strPythonPath = objFolder.Self.Path
End If
MsgBox strPythonPath
If Not fso.FileExists(strPythonPath & "\python.exe") Then
	MsgBox "δ�ҵ� python.exe, �ű��˳�"
	Wscript.Quit
End If

Rem 2.���ñ���·��
Set objShell = CreateObject("Shell.Application") 
Set objFolder = objShell.BrowseForFolder _ 
(WINDOW_HANDLE, "ǽֽ����·��:", OPTIONS, "")
If objFolder Is Nothing Then
	MsgBox "·����Ч, �ű��˳�"
	Wscript.Quit 
End If
strSavePath = objFolder.Self.Path : '����·����������\
If Not fso.FolderExists(strSavePath) Then
	fso.CreateFolder strSavePath
End If

Rem 3.����ű��� C:\scripts\
currentPath = createobject("Scripting.FileSystemObject").GetFile(Wscript.ScriptFullName).ParentFolder.Path
call CpFolder(fso, currentPath, strDepPath, True)

Rem 4.������������
Set WshShell = WScript.CreateObject("WScript.Shell")
strStartup = WshShell.SpecialFolders("Startup")
set oShellLink = WshShell.CreateShortcut(strStartup & "\dlbingwallpaper.lnk")
oShellLink.TargetPath = strPythonPath & "\python.exe"
oShellLink.Arguments = strDepPath & "\dlbingwallpaper.py " & strSavePath
oShellLink.WorkingDirectory = strDepPath
oShellLink.WindowStyle = 1 :'1 Ĭ�ϴ��� 3 ��� 7 ��С��
oShellLink.Description = ""
oShellLink.Save

Rem 5.����������������ݷ�ʽ
strStartup = WshShell.SpecialFolders("Desktop")
set oShellLink = WshShell.CreateShortcut(strStartup & "\wallpaperbrowser.lnk")
oShellLink.TargetPath = strPythonPath & "\python.exe"
oShellLink.Arguments = strDepPath & "\wallpaperbrowser.py " & strSavePath & " " & strDepPath
oShellLink.WorkingDirectory = strDepPath
oShellLink.WindowStyle = 1 :'1 Ĭ�ϴ��� 3 ��� 7 ��С��
oShellLink.Description = ""
oShellLink.Save

MsgBox "��װ��ɣ�"