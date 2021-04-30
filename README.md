# Music-Equalizer
- Sound equalizer is a basic tool in the music industry. It also serves in several biomedical applications like hearing aid industry.
 
## Description:
- It's a multiple document application. The window has two signal viewers display the signal “before” and “after” the equalization actions, the two viewers are linked. i.e. they show the same exact part of the signal if the user scroll or zoom on any one of them.
- The equalizer panel contains 10 sliders, each control the gain of 1/10 of the bandwidth of the frequency domain. The default value of each slider is 1 (i.e. the corresponding BW of the signal remain as is) and can go up to 5 and drop down to 0.
* Upon changing any equalizing slider, two things are expected to change:
   * The signal itself changes in the “After” viewer.
   * The spectrogram also is updated to reflect the change.
- To able to properly visualize the spectrogram, the user is able to control:
  * Min and max values (i.e. the pixels intensity range) to plot through two sliders for the min value and one for the max. Each slider should goes from min and max values of the spectrogram.
  * The color palette that is used in the spectrogram through a combo-box/drop-menu that has 5 different palettes to use from.
 
