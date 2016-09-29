rule evercookie : Evercookie Persistent_Cookie
{
    strings:
        $ec = "evercookie.js"
    condition:
        $ec
}
