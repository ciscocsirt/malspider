rule test3 : Neutrino_EK
{
    strings:
        $re1 = /^http:\/\/[^\x2f]+\.(?:cf|g[aq]|ml|tk|xyz)\/\/?(?=[^\x3f]+[a-z0-9]{17,})(?:[a-z0-9-]+\/){1,}(?:index\.php|[a-z]{3,10}\.[a-z]{2,4})?$/
        $re2 = /^http:\/\/[^\x2f]+\/[a-zA-Z0-9]{60,150}\/(?:index\.html)?$/
        $re3 = /^http:\/\/[^\x2f]+\/[a-z]{2}\/[a-zA-Z]\/[0-9]{2,4}\/$/

    condition:
        1 of ($re1,$re2,$re3)
}

rule test4 : Locky_Payload
{
     strings:
        $re1 = /^http:\/\/[^\x3f]+\/upload\/_dispatch\.php$/
     condition:
        $re1
}
