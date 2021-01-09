function exe-path {
    <# returns the path of the Live's application #>
    $exe = gp registry::hkcr\ableton\shell\open\command
    $exe.'(default)' -match '(.*)\s"%1"$' >$null
    $matches[1]
}

function start-live {
    <# starts Live #>
    if (!(ps 'Ableton Live*' -ea:0)) {ii $(exe-path)}
}

function stop-live {
    <# closes Live #>
    $exe = split-path (ps 'Ableton Live*').path -leaf
    taskkill /im $exe >$null
}

function restart-live {
    stop-live
    start-live
}

function live-data {
    <# useful data:
       - pschildname (GUID)
       - displayname (e.g. Ableton Live 10 Suite)
       - displayversion (e.g. 10.0.0.0 in 10.1.30)
       - version (e.g. 167772160 in 10.1.30)
       - installlocation (folder)
       - installdate (%Y%m%d)
    #>
    $apps = gp hklm:\software\microsoft\windows\currentversion\uninstall\*
    $apps |? publisher -eq Ableton
}
