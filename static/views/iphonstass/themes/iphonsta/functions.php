<?php
	function new_excerpt_length($length) {
		return 40;
	}
	add_filter('excerpt_length', 'new_excerpt_length');
	
	function new_excerpt_more($post) {
		return '...&nbsp;<span>(' . get_comments_number($post->ID) . ')</span>';

	}
	add_filter('excerpt_more', 'new_excerpt_more');


/*	function new_excerpt_length($length) {
//		return 40;
//	}
//	add_filter('excerpt_length', 'new_excerpt_length');
//	
//	function new_excerpt_more($post) {
//		return '...&nbsp;(' . get_comments_number($post->ID) . ')&nbsp;';
//
//	}
//	add_filter('excerpt_more', 'new_excerpt_more');
//
//
// Post thumbnail support */

add_theme_support( 'post-thumbnails' ); ?>