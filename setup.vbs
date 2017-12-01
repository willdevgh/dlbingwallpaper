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
DebugVersion = False
interpreter = "\pythonw.exe"
If DebugVersion Then
	interpreter = "\python.exe"
End If

Const WINDOW_HANDLE = 0 
Const OPTIONS = 0
strDepPath = "" :'��װ·��
Dim fso
Set fso = CreateObject("Scripting.FileSystemObject")

Rem 1.����python������·��
strPythonPath = GetPy3xPath()
If strPythonPath = "" Then
	Set objShell = CreateObject("Shell.Application") 
	Set objFolder = objShell.BrowseForFolder _ 
	(WINDOW_HANDLE, "Python������·��:", OPTIONS, "")
	If objFolder Is Nothing Then
		MsgBox "·����Ч, �ű��˳�", vbInformation, "����"
		Wscript.Quit 
	End If
    strPythonPath = objFolder.Self.Path
End If
MsgBox strPythonPath, vbInformation, "python������·��"
If Not fso.FileExists(strPythonPath & interpreter) Then
	MsgBox "δ�ҵ� pythonw.exe, �ű��˳�", vbInformation, "����"
	Wscript.Quit
End If

Rem 2.���ð�װ·��
Set objShell = CreateObject("Shell.Application") 
Set objFolder = objShell.BrowseForFolder _ 
(WINDOW_HANDLE, "��װ·��:", 0, "")
If objFolder Is Nothing Then
	MsgBox "·����Ч, �ű��˳�", vbInformation, "����"
	Wscript.Quit 
End If
strDepPath = objFolder.Self.Path :'��װ·����������\
If Not fso.FolderExists(strDepPath) Then
	fso.CreateFolder strDepPath
End If

Rem 3.���ñ���·��
Set objShell = CreateObject("Shell.Application") 
Set objFolder = objShell.BrowseForFolder _ 
(WINDOW_HANDLE, "ǽֽ����·��:", OPTIONS, "")
If objFolder Is Nothing Then
	MsgBox "·����Ч, �ű��˳�", vbInformation, "����"
	Wscript.Quit 
End If
strSavePath = objFolder.Self.Path :'����·����������\
If Not fso.FolderExists(strSavePath) Then
	fso.CreateFolder strSavePath
End If

Rem 4.����ű��� C:\scripts\
currentPath = createobject("Scripting.FileSystemObject").GetFile(Wscript.ScriptFullName).ParentFolder.Path
call CpFolder(fso, currentPath, strDepPath, True)

Rem 5.������������
Set WshShell = WScript.CreateObject("WScript.Shell")
strStartup = WshShell.SpecialFolders("Startup")
set oShellLink = WshShell.CreateShortcut(strStartup & "\dlbingwallpaper.lnk")
oShellLink.TargetPath = strPythonPath & interpreter
oShellLink.Arguments = strDepPath & "\dlbingwallpaper.py " & strSavePath
oShellLink.WorkingDirectory = strDepPath
oShellLink.WindowStyle = 1 :'1 Ĭ�ϴ��� 3 ��� 7 ��С��
oShellLink.Description = ""
oShellLink.Save

Rem 6.����������������ݷ�ʽ
strStartup = WshShell.SpecialFolders("Desktop")
set oShellLink = WshShell.CreateShortcut(strStartup & "\wallpaperbrowser.lnk")
oShellLink.TargetPath = strPythonPath & interpreter
oShellLink.Arguments = strDepPath & "\wallpaperbrowser.py " & strSavePath & " " & strDepPath
oShellLink.WorkingDirectory = strDepPath
oShellLink.WindowStyle = 1 :'1 Ĭ�ϴ��� 3 ��� 7 ��С��
oShellLink.Description = ""
oShellLink.Save

MsgBox "��װ��ɣ�", vbInformation, "setup"