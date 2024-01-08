$directory=$args[0]
$directory_plugins_xml=$args[1]
$Version_old=$args[2]
$Version_new=$args[3]

$Path_xml = "$($directory_plugins_xml)\plugins_exp.xml"
$source="plugin_id=""$($directory)"" version=""$($Version_old)"""
$target="plugin_id=""$($directory)"" version=""$($Version_new)"""

#Write-Host $Path_xml
#Write-Host $source
#Write-Host $target

(Get-Content -Path $Path_xml) -replace $source,$target | Set-Content -Path $Path_xml