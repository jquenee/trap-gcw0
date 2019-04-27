# trap-gcw0
Trap TO7 game adaptation 

# pygame installation in MacOS
https://github.com/pygame/pygame/issues/555

````
brew install sdl2 sdl2_gfx sdl2_image sdl2_mixer sdl2_net sdl2_ttf
cd /usr/local/lib/python2.7/site-packages/
rm -rf pygame*
git clone https://github.com/pygame/pygame.git
cd pygame
python setup.py -config -auto -sdl2
python setup.py install
````

# launch game in MacOS / Linux
````
git clone https://github.com/jquenee/trap-gcw0.git
cd trap-gcw0
./src/main.py
````
