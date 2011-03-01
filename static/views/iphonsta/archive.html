<?php get_header(); ?>
				  <?php /* If this is a category archive */ if (is_category()) { ?>
                    <div class="pagetitle"><?php printf(__('&#8216;%s&#8217; Category'), single_cat_title('', false)); ?></div>
                  <?php /* If this is a tag archive */ } elseif( is_tag() ) { ?>
                    <div class="pagetitle"><?php printf(__('&#8216;%s&#8217;'), single_tag_title('', false) ); ?></div>
                  <?php /* If this is a daily archive */ } elseif (is_day()) { ?>
                    <div class="pagetitle"><?php printf(_c('%s|Daily archive page'), get_the_time(__('F jS, Y'))); ?></div>
                  <?php /* If this is a monthly archive */ } elseif (is_month()) { ?>
                    <div class="pagetitle"><?php printf(_c('%s|Monthly archive page'), get_the_time(__('F, Y'))); ?></div>
                  <?php /* If this is a yearly archive */ } elseif (is_year()) { ?>
                    <div class="pagetitle"><?php printf(_c('%s|Yearly archive page'), get_the_time(__('Y'))); ?></div>
                  <?php /* If this is an author archive */ } elseif (is_author()) { ?>
                    <div class="pagetitle"><?php _e('Author Archive'); ?></div>
                  <?php /* If this is a paged archive */ } elseif (isset($_GET['paged']) && !empty($_GET['paged'])) { ?>
                    <div class="pagetitle"><?php _e('Blog Archives'); ?></div>
                  <?php } ?>
        <div id="cnt">
        
<?php if (have_posts()) : ?>
	<?php while (have_posts()) : the_post();$first++; ?>
		<?php if ( 1 == $first && !is_paged() ) { ?>
        
                  	<a class="art" href="<?php the_permalink() ?>" id="post-<?php the_ID(); ?>">
	
                    	<?php
                    	$imgsrcparam = array(
						'class'	=> "prv",
						'alt'	=> trim(strip_tags( $post->post_excerpt )),
						'title'	=> trim(strip_tags( $post->post_title )),
						);
                    	$thumbID = get_the_post_thumbnail( $post->ID, 'thumbnail', $imgsrcparam ); ?>
                        <h2><?php the_title(); ?></h2>
                        
                     	<?php echo "$thumbID"; ?>
                        
                        <?php the_excerpt(); ?>
                    </a>

          <?php } elseif ( 2 == $first && !is_paged() ) { ?>
          
                    	<?php
                    	$imgsrcparam = array(
						'class'	=> "prv",
						'alt'	=> trim(strip_tags( $post->post_excerpt )),
						'title'	=> trim(strip_tags( $post->post_title )),
						);
                    	$thumbID = get_the_post_thumbnail( $post->ID, 'thumbnail', $imgsrcparam ); ?>
                    	
                    <a class="art" href="<?php the_permalink() ?>" id="post-<?php the_ID(); ?>">
                        <h2><?php the_title(); ?></h2>
    
	                    <?php echo "$thumbID"; ?>
                        
                        <?php the_excerpt(); ?>
                    </a>
          
          <?php } else { ?>
         
                <a class="art sm" href="<?php the_permalink() ?>">
                    <h2><?php the_title(); ?></h2><?php comments_number('<span>0</span>','<span>1</span>','<span>%</span>'); ?>
                </a>

          <?php } ?>
 
	<?php endwhile; ?>
<?php endif; ?>
               
        
        
        
  

		<?php if(function_exists('wp_pagenavi')) { wp_pagenavi(); } ?>
        
        
        


        
        </div>
<?php get_footer(); ?>