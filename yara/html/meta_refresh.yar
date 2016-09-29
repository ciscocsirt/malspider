rule meta_refresh : Meta_Refresh
{
    strings:
        $meta_refresh = /(<meta(?=[^>]*?http-equiv)(?=[^>]*?refresh)(?=[^>]*?url).*?>)/
    condition:
        $meta_refresh
}

