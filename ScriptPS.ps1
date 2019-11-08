$ruta=$args[0]
$cadena=(select-string -path $ruta\metadata.txt -Pattern 'version=' -CaseSensitive);
($cadena -split "=")[1]

