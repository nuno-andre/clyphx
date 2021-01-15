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
    $exe = ps 'Ableton Live*'
    if ($exe) {taskkill /im $(split-path $exe.path -leaf) >$null}
}

function restart-live {
    stop-live
    sleep 5
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

# FIXME: hard-coded path
function open-log {
    $path = join-path ${env:APPDATA} 'Ableton\Live 10.1.30\Preferences\Log.txt'
    start $path
}

function install-runtime {
    $url = 'https://www.python.org/ftp/python/2.7.18/python-2.7.18.amd64.msi'
    $dest = join-path (gi $psscriptroot).parent.fullname .bin

    if (!(mkdir .bin -ea:0)) {
        echo '.\.bin folder already exists. Installation canceled.'
    } else {
        echo 'Downloading Python 2.7 installer...'
        curl.exe -`#OL $url

        echo 'Extracting runtime...'
        $unc = join-path '\\localhost' $($dest -replace ':', '$')
        $file = split-path $url -leaf
        msiexec /a $file TARGETDIR=$unc

        echo 'Removing installer...'
        rm $file -f

        echo 'Installation succeeded.'
    }
}

function install-dev-script {
    <# creates symlink to source directory in Live's scripts dir #>
    $base = (gi $(exe-path)).directory.parent.fullname
    $link = join-path $base 'Resources\MIDI Remote Scripts\ClyphXDev'
    $target = join-path (gi $psscriptroot).parent.fullname 'src/clyphx'
    cmd /c mklink /D $link $target
}
