# Unique Tile Remover
![Unique Tile Remover logo](https://github.com/bolon667/removeUniqueTilesFromImage/blob/main/gitPics/reduceUniqueTiles_logo.jpg)

Python script which reducing amount of unique tiles in image (useful for retro development)

# Comparison
**Click** to see full picture
![Compare](https://github.com/bolon667/removeUniqueTilesFromImage/blob/main/gitPics/comparePic.png)

# How to use
1. Download python script
2. Put your image in script folder, and rename it to **map.png**
3. Change quality in python script of reducer.reduceTilesetSizeBySimilarity(0.3) for your needs (value from 0.2 to 1.0)
4. Run script, result will be in **result.png** file, in script folder
# How it works
1. Generating tileset from image
2. Generating tilemap from image (2D array)
3. Generating reduced tileset according to this formula: tile_size = cell_size*quality
4. Comparing every tile with every tile in reduced tileset, if tiles are equal, then merghing tiles. Merged tile putting from reduced tileset to original tileset
5. Recreating image back, from tileset and tilemap.
6. Done

