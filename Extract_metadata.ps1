$ruta=$args[0]
$path_Destino=$args[1]
$plugin=$args[2]

$sourceFile=$ruta
Add-Type -Assembly System.IO.Compression.FileSystem
# load ZIP methods
$zip = [IO.Compression.ZipFile]::OpenRead($sourceFile)
$entries = $zip.Entries | where {$_.Name -eq 'metadata.txt'}
$entries | foreach {[System.IO.Compression.ZipFileExtensions]::ExtractToFile($_,$path_Destino+'\metadata.txt' , $true)}
$zip.Dispose()