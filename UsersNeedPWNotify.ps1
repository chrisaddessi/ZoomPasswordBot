#Make so only in Active users
Import-Module ActiveDirectory
$allusers = Get-ADUser -SearchBase "REDACTED" -Filter *
$MaxPwdAge = (Get-ADDefaultDomainPasswordPolicy).MaxPasswordAge.Days
$currentdatel = Get-Date
$currentdate = $currentdatel.ToShortDateString()
$currentdate = get-date $currentdate


$14days_ = @()
$7days_ = @()
$3days_ = @()
$errorcount = 0

$outfile = "UsersToBeNotified.csv"
$errors = "Errors-PS.log"

foreach ($user in $allusers){
    #Check to see if password will expire in 2 weeks
    try{
        $lastset = Get-ADUser -identity $user -Properties PasswordLastSet | Select-Object -ExpandProperty passwordlastset
        $expires=$lastset.AddDays($MaxPwdAge) # expires
        $expiresu = Get-Date -Format "dddd MM/dd/yyyy hh:mm tt" $expires
        $expires = $expires.ToShortDateString()
        $expires = get-date $expires
    
        if ($expires -eq $currentdate.AddDays(14)){$14days_ += (Get-AdUser $user -Properties *).EmailAddress  + "," + $expiresu ;}
        if ($expires -eq $currentdate.AddDays(7)){$7days_ += (Get-AdUser $user -Properties *).EmailAddress + "," + $expiresu;}
        if ($expires -le $currentdate.AddDays(3) -and $expires -ge $currentdate.AddDays(0)){ $3days_ += (Get-AdUser $user -Properties *).EmailAddress + "," + $expiresu;}
    }
    catch{
        $errorstring = $user.UserPrincipalName + "," + $currentdatel
        echo "Password expireation date error: $errorstring" > $errors
        $errorcount ++
    }

    
}

Write-Host "Account Name,Expiration,Days" > $outfile

foreach ($user in $14days_){
    $user = $user.Split(",")
    $upnstring =  $user[0] + "," + $user[1] + ",14"
    echo $upnstring.GetType()
    $upnstring >> $outfile
}
foreach ($user in $7days_){
    $user = $user.Split(",")
    $upnstring =  $user[0] + "," + $user[1] + ",7"
    $upnstring >> $outfile
}
foreach ($user in $3days_){
    $user = $user.Split(",")
    $upnstring =  $user[0] + "," + $user[1] + ",3"
    $upnstring >> $outfile
}

Write-Host "Number of errors: " $errorcount