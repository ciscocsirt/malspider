rule scanbox : Scanbox_Framework
{
    strings:
        $scanbox1 = /^.*\/[a-zA-Z]{1}\/\?[0-9]{1,2}$/
        $scanbox2 = /^.*\/[a-zA-Z]{1}\/recv\.php$/
        $scanbox3 = /^.*\/[a-zA-Z]{1}\/[a-zA-Z]{1}\.php(\?[a-zA-Z]{5}_[a-zA-Z]{5}==[0-9]{1,2})?$/
    condition:
        $scanbox1 or $scanbox2 or $scanbox3
}
