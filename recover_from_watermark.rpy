while True:
    test_videos=rp_glob('tests/*.mp4')
    
    import numpy as np
    
    def recover_background(composite_images, rgba_watermark):
        # Ensure the images are in the correct float32 format ranging from 0 to 1
        composite_images = composite_images.astype(np.float32)
        rgba_watermark = rgba_watermark.astype(np.float32)
        
        # Extract RGB and Alpha components of the watermark
        rgb_watermark = rgba_watermark[:, :, :3]
        alpha_watermark = rgba_watermark[:, :, 3]
        
        # Expand alpha to work across color channels
        alpha_watermark = np.expand_dims(alpha_watermark, axis=-1)
        
        # Calculate the background image using the derived formula
        # Use np.clip to ensure the resulting pixel values are still in the range [0, 1]
        background = (composite_images - alpha_watermark * rgb_watermark) / (1 - alpha_watermark)
        background = np.clip(background, 0, 1)
        
        return background
    #video=load_video('shutter_cracker.webm',use_cache=True)/255
    video=load_video('/Users/ryan/Downloads/vid2.mp4',use_cache=True)/255
    video=load_video(random_element(test_videos),use_cache=True)/255
    #video=load_video(ans,use_cache=False)/255
    #video=video[::10]
    video=as_numpy_array(resize_list(video,length=60))
    #video=video[as_numpy_array(resize_list(range(len(video)),length=60))]
    watermark=load_image('watermark.exr',use_cache=True)
    
    avg_frame=video.mean(0)
    
    watermark=crop_image(watermark,*get_image_dimensions(avg_frame)) #Sometimes not a perfect match...
    
    best_watermark=None
    best_edges_mean=10000
    best_x_shift=None
    best_y_shift=None
    shift_range=5
    shifts=range(-shift_range,shift_range+1)
    for x_shift in shifts:
        for y_shift in shifts:
            #shifted_watermark=crop_image(shift_image(watermark,x=x_shift,y=y_shift,allow_growth=False),*get_image_dimensions(avg_frame),origin='bottom right')
            shifted_watermark=np.roll(np.roll(watermark,x_shift,axis=1),y_shift,axis=0)
            recovered_frame=recover_background(avg_frame[None],shifted_watermark)[0]
            
            #SLOW!            
            #edges=sobel_edges(recovered_frame)#TODO:Make faster
            
            edges=recovered_frame
            edges=np.diff(np.diff(edges,axis=0),axis=1)**2*100
            

            edges_mean=edges.mean()
            if edges_mean<best_edges_mean:
                best_edges_mean=edges_mean
                best_watermark=shifted_watermark
                best_x_shift=x_shift
                best_y_shift=y_shift
            
            print(x_shift,y_shift,edges.mean())
            display_image(edges)
            #input('>>>')
    
    
    recovered=recover_background(video,best_watermark)
    analy_video=vertically_concatenated_videos(recovered,video)
    analy_video=labeled_images(analy_video,'dx=%i   dy=%i'%(best_x_shift,best_y_shift))
    save_video_mp4(analy_video,get_unique_copy_path('comparison_video.mp4'),framerate=30)
    display_video(analy_video)