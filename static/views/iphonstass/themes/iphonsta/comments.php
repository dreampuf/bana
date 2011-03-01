<?php
/**
 * @package WordPress
 */

// Do not delete these lines
	if (isset($_SERVER['SCRIPT_FILENAME']) && 'comments.php' == basename($_SERVER['SCRIPT_FILENAME']))
		die ('Please do not load this page directly. Thanks!');
	
	if ( post_password_required() ) { ?>
		<p class="nocomments"><?php _e('This post is password protected. Enter the password to view comments.'); ?></p> 
	<?php
		return;
	}
?>

<!-- You can start editing here. -->
<?php if ( have_comments() ) : ?>
    <a name="comments"></a>

	<div class="navigation">
		<div class="alignleft"><?php previous_comments_link() ?></div>
		<div class="alignright"><?php next_comments_link() ?></div>
	</div>

	<ol class="commentlist">



		<?php foreach ($comments as $comment) : ?>
            <li <?php comment_class(); ?> id="comment-<?php comment_ID() ?>">
            <div class="comment-author-info"><span class="comment-author"><?php comment_author() ?></span>, <?php comment_date('d F, Y') ?><?php edit_comment_link(__("Edit This"), ' | '); ?></div>
            <?php comment_text() ?>
            <div class="hr"></div>
            </li>
        
        <?php endforeach; ?>



	</ol>

	<div class="navigation">
		<div class="alignleft"><?php previous_comments_link() ?></div>
		<div class="alignright"><?php next_comments_link() ?></div>
	</div>
 <?php else : // this is displayed if there are no comments so far ?>

	<?php if ( comments_open() ) : ?>
		<!-- If comments are open, but there are no comments. -->

	 <?php else : // comments are closed ?>
		<!-- If comments are closed. -->
		<p class="nocomments"><?php _e('Comments are closed.'); ?></p>

	<?php endif; ?>
<?php endif; ?>


<?php if ( comments_open() ) : ?>

<div id="respond">


<?php if ( is_user_logged_in() ) : ?>

<div class="login"><?php printf(__('Logged in as <a href="%1$s">%2$s</a>.'), get_option('siteurl') . '/wp-admin/profile.php', $user_identity); ?> <a href="<?php echo wp_logout_url(get_permalink()); ?>" title="<?php _e('Log out of this account'); ?>"><?php _e('Log out &raquo;'); ?></a></div>

<?php endif; ?>





<div id="cancel-comment-reply"> 
	<small><?php cancel_comment_reply_link() ?></small>
</div> 
<?php if ( is_user_logged_in() ) : ?>


<?php else : ?>



<div id="uit">
  <input type="text" name="author" id="author"  onfocus="if(this.value=='Name') this.value='';" onblur="if(this.value=='') this.value='Name';" value="Name" size="22" tabindex="1" <?php if ($req) echo "aria-required='true'"; ?> />
  <input type="text" name="email" id="email"  onfocus="if(this.value=='E-Mail: (required)') this.value='';" onblur="if(this.value=='') this.value='E-Mail: (required)';" value="E-Mail: (required)" size="22" tabindex="2" <?php if ($req) echo "aria-required='true'"; ?> />
    
<!--    <div class="outbl"><input type="text" name="url" id="url"  onfocus="if(this.value=='Website URL') this.value='';" onblur="if(this.value=='') this.value='Website URL';" value="Website URL" size="22" tabindex="3" /></div>-->
</div>
<?php endif; ?>

<?php if ( get_option('comment_registration') && !is_user_logged_in() ) : ?>
<p><?php printf(__('You must be <a href="%s">logged in</a> to post a comment.'), wp_login_url( get_permalink() )); ?></p>
<?php else : ?>

<form action="<?php echo get_option('siteurl'); ?>/wp-comments-post.php" method="post" id="commentform">

<textarea name="comment" id="comment" cols="100%" rows="10" tabindex="4"></textarea>



<!--<p><small><?php printf(__('<strong>XHTML:</strong> You can use these tags: <code>%s</code>'), allowed_tags()); ?></small></p>-->


<div class="submit"><div class="outbl sbm"><input name="submit" type="submit" id="submit" tabindex="5" value="Submit comment" /></div>
<?php comment_id_fields(); ?> 
</div>
<?php do_action('comment_form', $post->ID); ?>

</form>

<?php endif; // If registration required and not logged in ?>
</div>

<?php endif; // if you delete this the sky will fall on your head ?>
