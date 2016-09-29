rule clicky : Clicky_Malware
{
    strings:
        $clicky1 = "var clicky_site_ids"
        $clicky2 = "clicky_site_ids.push("

    condition:
        $clicky1 or $clicky2
}
