# Helps me deploy


function Get-VersionNumber {
    (Get-Content .\ChordEvents\__version__.py) -match "(?<=`")([0-9])\.([0-9])\.([0-9])(?=`")"
    return [PSCustomObject]@{
        Major = [int]$matches.1
        Minor = [int]$matches.2
        Build = [int]$matches.3
    }
}


function Set-VersionNumber {
    param(
        [Parameter(Mandatory=$true)]
        [int]
        $Major,
        
        [Parameter(Mandatory=$true)]
        [int]
        $Minor,

        [Parameter(Mandatory=$true)]
        [int]
        $Build
    )
    Set-Content .\ChordEvents\__version__.py "__version__ = `"$Major.$Minor.$Build`""
}

$v = Get-VersionNumber
Write-Output "Current version $($v.Major).$($v.Minor).$($v.Build).  Increment Major(1), Minor(2), Build(3), or skip this part(4)?"
$user_input = Read-Host
if ($user_input -eq 1) {
    Set-VersionNumber ($v.Major + 1) $v.Minor $v.Build
}
elseif ($user_input -eq 2) {
    Set-VersionNumber $v.Major ($v.Minor + 1) $v.Build
}
elseif ($user_input -eq 3) {
    Set-VersionNumber $v.Major $v.Minor ($v.Build + 1)
}
elseif ($user_input -eq 4) {
    Write-Output "Skipped updating version number"
}
else {
    Write-Error "Invalid user input, expected 1, 2, 3, or 4"
}

# Get PyPi answer, needs to be before setup.py so that we can clear the dist directory
Write-Output "Push to PyPi(1), PyPi Test(2), or skip this part(3)"
$pypi = Read-Host
if ($pypi -ne 3) {
    Remove-Item -Recurse .\dist\*
}

# Get commit message
Write-Output "Enter commit message, or 'none' to skip commit"
$commit_msg = Read-Host

# Build docs
.\docs\make.bat html
if (-not $?) { 
    Write-Error "Failed when building documentation"
    exit 
}

# Build wheel
.\setup.py sdist bdist_wheel
if (-not $?) { 
    Write-Error "Failed when building wheel"
    exit 
}

# Do git stuff
if ($commit_msg -ne "none") {
    git add .
    git commit -m $commit_msg
    git push
}
else {
    Write-Output "Skipped git commit"
}

# Do PyPi stuff
if ($pypi -eq 1) {
    Write-Output "`n`n`nStarting PyPi upload, may need to enter your username and password"
    python -m twine upload dist/*
}
elseif ($pypi -eq 2) {
    Write-Output "`n`n`nStarting PyPi upload, may need to enter your username and password"
    python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
}
elseif ($pypi -eq 3) {
    Write-Output "Skipped deploying to PyPi"
}

Write-Output "Deploy success, exiting in 5 seconds"
Start-Sleep 5