<!DOCTYPE html PUBLIC "-//WAPFORUM//DTD XHTML Mobile 1.0//EN" "http://www.wapforum.org/DTD/xhtml-mobile10.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
	<title><?php bloginfo('name'); ?><?php wp_title(); ?></title>
    <meta name="viewport" content="width=device-width, minimum-scale=1.0, maximum-scale=1.0, user-scalable=no" />
	<meta name="generator" content="WordPress <?php bloginfo('version'); ?>" /> <!-- leave this for stats please -->

	<link rel="stylesheet" href="<?php bloginfo('template_url'); ?>/reset.css" type="text/css" media="screen" />
	<link rel="stylesheet" href="<?php bloginfo('stylesheet_url'); ?>" type="text/css" media="screen" />
    
    <link rel="shortcut icon" href="<?php bloginfo('template_url'); ?>/favicon.ico" type="image/x-icon" />
    <link rel="alternate" type="application/rss+xml" title="RSS 2.0" href="<?php bloginfo('rss2_url'); ?>" />
	<link rel="alternate" type="text/xml" title="RSS .92" href="<?php bloginfo('rss_url'); ?>" />
	<link rel="alternate" type="application/atom+xml" title="Atom 0.3" href="<?php bloginfo('atom_url'); ?>" />
	<link rel="pingback" href="<?php bloginfo('pingback_url'); ?>" />
    <?php wp_head(); ?>
    
	<script type="text/javascript">
    <!--
        function toggle_visibility(id) {
           var e = document.getElementById(id);
           if(e.style.display == 'block')
              e.style.display = 'none';
           else
              e.style.display = 'block';
        }
        function changeCssClass(objDivID)
        {
            if(document.getElementById(objDivID).className=='active')
            {
                document.getElementById(objDivID).className = '';
            }
            else
            {
                document.getElementById(objDivID).className = 'active';
            }
        }
	//-->
    </script>
</head>
<body <?php body_class(); ?>>
	<div id="out">
        <div id="inner">
    	<div id="hd">
        	<a href="<?php bloginfo("url"); ?>" id="lg"></a>
            <ul id="tpmn">
            	<li id="cts"><a href="JavaScript:;" onclick="toggle_visibility('top-menu'); changeCssClass('cts'); getElementById('top-menu2').style.display='none'; getElementById('pg').setAttribute('class', '');"><b>Categories</b></a></li>
            	<li id="pg"><a href="JavaScript:;" onclick="toggle_visibility('top-menu2'); changeCssClass('pg'); getElementById('top-menu').style.display='none'; getElementById('cts').setAttribute('class', '');"><b>Pages</b></a></li>
            </ul>
        </div>
        <ul id="top-menu" style="display:none;">
            <?php
                $data = wp_list_categories('show_count=1&echo=0&title_li=0&depth=1');
                $data = preg_replace('/\<\/a\> \((.*)\)/',' <span>$1</span></a>',$data);
                echo $data;
            ?>
        </ul>
        <ul id="top-menu2" style="display:none;">
            <?php wp_list_pages('title_li=0&depth=1'); ?>
        </ul>
