from PIL import Image, ImageDraw
from PIL import ImageChops
import glob
from enum import Enum

class FlipValues(Enum):
   NONE = 0,
   FLIP_LEFT_RIGHT = 1,
   FLIP_TOP_BOTTOM = 2,
   FLIP_TOP_BOTTOM_AND_FLIP_LEFT_RIGHT = 3

class SimilarityAlghorithm(Enum):
    EQUAL_PIXELS = 0, #not very good
    EQUAL_PIXELS_ON_REDUCED_RESOLUTION = 1, #slightly better
    DOMINANT_COLOR = 2, #idk, mb better
    TEST_ALG = 3,
    TEST_ALG2 = 4,
    EQUAL_PIXELS_ON_REDUCED_RESOLUTION_V2 = 5, #a lot better
    EQUAL_PIXELS_ON_REDUCED_RESOLUTION_V2_TEST = 6,
    EQUAL_PIXELS_ON_REDUCED_RESOLUTION_V2_TTT=7,

class uniqueTileReducer():
  src_img = None
  src_img_pal = None
  src_img_amount_of_colors = 0
  tileset = []
  resizedTileset = []
  resizedTileset2 = []
  resizedTileset3 = []
  resizedTileset4 = []

  src_img_path = ""
  cell_size = 8

  similarity_method = SimilarityAlghorithm.DOMINANT_COLOR

  tile_population = []
  tilemap = []
  flipmap = []



  def __init__(self, src_img_path, sim_method = SimilarityAlghorithm.DOMINANT_COLOR, cell_size = 8):
    self.src_img_path = src_img_path
    self.cell_size = cell_size
    self.similarity_method = sim_method
    self.src_img = Image.open(src_img_path)
    self.src_img_pal = self.src_img.getpalette()
    self.src_img_amount_of_colors = int(len(self.src_img.getpalette())/3)
    self.gen_empty_tilemap()
    self.gen_empty_flipmap()
    print("Image is loaded")
  def gen_empty_tilemap(self):
    self.tilemap = []
    img_size = self.src_img.size
    cols = int(img_size[0]/self.cell_size)
    rows = int(img_size[1]/self.cell_size)
    for tileY in range(0, rows):
      temp_arr = []
      for tileX in range(0, cols):
        temp_arr.append(0)
      self.tilemap.append(temp_arr)
  def gen_empty_flipmap(self):
    self.flipmap = []
    img_size = self.src_img.size
    cols = int(img_size[0]/self.cell_size)
    rows = int(img_size[1]/self.cell_size)
    for tileY in range(0, rows):
      temp_arr = []
      for tileX in range(0, cols):
        temp_arr.append(FlipValues.NONE)
      self.flipmap.append(temp_arr)
  def reduceTilesetSizeBySimilarity(self, threshold = 0.8):
    print("Similarity method: ", self.similarity_method)
    if(self.similarity_method == SimilarityAlghorithm.EQUAL_PIXELS):
        #compate every tile with every tile
        for tileInd in range(len(self.tileset)):
            for testTileInd in range(tileInd+1, len(self.tileset)):
                equal_perc = self.getImageEqualPercent(self.tileset[tileInd], self.tileset[testTileInd])
                is_same_dom_color, who_have_more_colors, is_colors_same_on_2_images = self.isImagesHaveColors(self.tileset[tileInd], self.tileset[testTileInd])
                if not is_same_dom_color:
                   continue
                if((equal_perc >= threshold)):
                    # print(equal_perc)
                    #self.tile_population[tileInd] < self.tile_population[testTileInd]
                    if(self.tile_population[tileInd] < self.tile_population[testTileInd]):
                        self.tileset[tileInd] = self.tileset[testTileInd]
                    else:
                        self.tileset[testTileInd] = self.tileset[tileInd]
    elif(self.similarity_method == SimilarityAlghorithm.EQUAL_PIXELS_ON_REDUCED_RESOLUTION):
        #reduce every tile size
        new_res = [int(self.cell_size*threshold), int(self.cell_size*threshold)]
        if new_res[0] == 0:
           new_res = 1
        if new_res[1] == 0:
           new_res = 1
        self.resizedTileset = []
        for tileInd in range(len(self.tileset)):
           self.resizedTileset.append(self.tileset[tileInd].resize([new_res[0], new_res[1]], Image.NEAREST))
        for tileInd in range(len(self.tileset)):
            for testTileInd in range(tileInd+1, len(self.tileset)):
                equal_perc = self.getImageEqualPercent(self.resizedTileset[tileInd], self.resizedTileset[testTileInd])
                is_same_dom_color, who_have_more_colors, is_colors_same_on_2_images = self.isImagesHaveColors(self.tileset[tileInd], self.tileset[testTileInd])
                if not is_colors_same_on_2_images:
                   continue
                if((equal_perc >= 0.90) and is_same_dom_color): #0.75
                    # print(equal_perc)
                    if((self.tile_population[tileInd] < self.tile_population[testTileInd]) and who_have_more_colors and is_colors_same_on_2_images):
                        self.tileset[tileInd] = self.tileset[testTileInd]
                    else:
                        self.tileset[testTileInd] = self.tileset[tileInd]
    elif(self.similarity_method == SimilarityAlghorithm.DOMINANT_COLOR):
       #compate every tile with every tile
        for tileInd in range(len(self.tileset)):
            for testTileInd in range(tileInd+1, len(self.tileset)):
                is_same_dom_color, _, _ = self.isImagesHaveColors(self.tileset[tileInd], self.tileset[testTileInd])
                equal_perc = self.getImageEqualPercent(self.tileset[tileInd], self.tileset[testTileInd])
                if((equal_perc >= threshold) and is_same_dom_color):
                    # print(equal_perc)
                    if(self.tile_population[tileInd] < self.tile_population[testTileInd]):
                        self.tileset[tileInd] = self.tileset[testTileInd]
                    else:
                        self.tileset[testTileInd] = self.tileset[tileInd]
    elif(self.similarity_method == SimilarityAlghorithm.TEST_ALG):
        for tileInd in range(len(self.tileset)):
            max_equal_perc = -1
            saved_testTileInd = -1
            save_who_have_more_colors = False
            #Finding most similar tile to current tile
            for testTileInd in range(tileInd+1, len(self.tileset)):
                is_same_dom_color, who_have_more_colors, is_same_colors = self.isImagesHaveColors(self.tileset[tileInd], self.tileset[testTileInd])
                equal_perc = self.getImageEqualPercent(self.tileset[tileInd], self.tileset[testTileInd])
                if((equal_perc >= threshold) and (equal_perc > max_equal_perc) and is_same_dom_color):
                   max_equal_perc = equal_perc
                   saved_testTileInd = testTileInd
                   save_who_have_more_colors = who_have_more_colors
            #If most similar tile, similarity rate >= threshold, then changing tiles
            if(max_equal_perc >= threshold):
                 # print(equal_perc)
                 #self.tile_population[tileInd] < self.tile_population[saved_testTileInd]
                if((self.tile_population[tileInd] < self.tile_population[saved_testTileInd]) or save_who_have_more_colors):
                    self.tileset[tileInd] = self.tileset[saved_testTileInd]
                else:
                    self.tileset[saved_testTileInd] = self.tileset[tileInd]
    elif(self.similarity_method == SimilarityAlghorithm.TEST_ALG2):
        new_res = [int(self.cell_size*threshold), int(self.cell_size*threshold)]
        if new_res[0] == 0:
           new_res = 1
        if new_res[1] == 0:
           new_res = 1
        self.resizedTileset = []
        for tileInd in range(len(self.tileset)):
           self.resizedTileset.append(self.tileset[tileInd].resize([new_res[0], new_res[1]], Image.NEAREST))

        for tileInd in range(len(self.tileset)):
            max_equal_perc = -1
            saved_testTileInd = -1
            saved_is_colors_equal = False
            save_who_have_more_colors = False
            #Finding most similar tile to current tile
            for testTileInd in range(tileInd+1, len(self.tileset)):
                is_same_dom_color, who_have_more_colors, is_same_colors = self.isImagesHaveColors(self.resizedTileset[tileInd], self.resizedTileset[testTileInd])
                equal_perc = self.getImageEqualPercent(self.resizedTileset[tileInd], self.resizedTileset[testTileInd])
                if((equal_perc >= threshold) and (equal_perc > max_equal_perc) and is_same_dom_color and is_same_colors):
                   # and is_same_dom_color
                   max_equal_perc = equal_perc
                   saved_testTileInd = testTileInd
                   save_who_have_more_colors = who_have_more_colors
                   saved_is_colors_equal = is_same_colors
            #If most similar tile, similarity rate >= threshold, then changing tiles
            if((max_equal_perc >= 0.95)): #0.75
              # print(equal_perc)
              if((self.tile_population[tileInd] < self.tile_population[saved_testTileInd])):
                self.tileset[tileInd] = self.tileset[saved_testTileInd]
              else:
               self.tileset[saved_testTileInd] = self.tileset[tileInd]
    elif(self.similarity_method == SimilarityAlghorithm.EQUAL_PIXELS_ON_REDUCED_RESOLUTION_V2):
       #reduce every tile size
        new_res = [int(self.cell_size*threshold), int(self.cell_size*threshold)]
        if new_res[0] == 0:
           new_res = 1
        if new_res[1] == 0:
           new_res = 1
        self.resizedTileset = []
        self.resizedTileset2 = []
        self.resizedTileset3 = []
        self.resizedTileset4 = []

        for tileInd in range(len(self.tileset)):
           self.resizedTileset.append(self.tileset[tileInd].resize([new_res[0], new_res[1]], Image.NEAREST))
        for tileInd in range(len(self.tileset)):
           self.resizedTileset2.append(self.tileset[tileInd].resize([new_res[0], new_res[1]], Image.NEAREST).transpose(Image.FLIP_LEFT_RIGHT))
        for tileInd in range(len(self.tileset)):
           self.resizedTileset3.append(self.tileset[tileInd].resize([new_res[0], new_res[1]], Image.NEAREST).transpose(Image.FLIP_TOP_BOTTOM))
        for tileInd in range(len(self.tileset)):
           self.resizedTileset4.append(self.tileset[tileInd].resize([new_res[0], new_res[1]], Image.NEAREST).transpose(Image.FLIP_TOP_BOTTOM).transpose(Image.FLIP_LEFT_RIGHT))
          #  self.tileset[tileInd] = self.tileset[tileInd].resize([new_res[0], new_res[1]], Image.NEAREST)
        for tileInd in range(len(self.tileset)):
            for testTileInd in range(tileInd+1, len(self.tileset)):
                equal_perc = self.getImageEqualPercent(self.resizedTileset[tileInd], self.resizedTileset[testTileInd])
                test_perc = self.getImageEqualPercent(self.resizedTileset2[tileInd], self.resizedTileset2[testTileInd])
                if test_perc > equal_perc:
                  equal_perc = test_perc
                test_perc = self.getImageEqualPercent(self.resizedTileset3[tileInd], self.resizedTileset3[testTileInd])
                if test_perc > equal_perc:
                  equal_perc = test_perc
                test_perc = self.getImageEqualPercent(self.resizedTileset4[tileInd], self.resizedTileset4[testTileInd])
                if test_perc > equal_perc:
                  equal_perc = test_perc

                is_same_dom_color, who_have_more_colors, is_colors_same_on_2_images = self.isImagesHaveColors(self.tileset[tileInd], self.tileset[testTileInd])
                # if not is_colors_same_on_2_images:
                #    continue
                if((equal_perc >= 0.60)): #0.75
                    # print(equal_perc)
                    if((self.tile_population[tileInd] < self.tile_population[testTileInd]) and who_have_more_colors and is_colors_same_on_2_images):
                        self.tileset[tileInd] = self.resizedTileset[testTileInd].resize([self.cell_size, self.cell_size], Image.NEAREST)
                    else:
                        self.tileset[testTileInd] = self.resizedTileset[testTileInd].resize([self.cell_size, self.cell_size], Image.NEAREST)
    elif(self.similarity_method == SimilarityAlghorithm.EQUAL_PIXELS_ON_REDUCED_RESOLUTION_V2_TTT):
       #reduce every tile size
        new_res = [int(self.cell_size*threshold), int(self.cell_size*threshold)]
        if new_res[0] == 0:
           new_res = 1
        if new_res[1] == 0:
           new_res = 1
        self.resizedTileset = []
        for tileInd in range(len(self.tileset)):
           self.resizedTileset.append(self.tileset[tileInd].resize([new_res[0], new_res[1]], Image.NEAREST))
          #  self.tileset[tileInd] = self.tileset[tileInd].resize([new_res[0], new_res[1]], Image.NEAREST)
        tileInd = 0
        while tileInd < len(self.tileset):
            testTileInd = tileInd+1
            while testTileInd < len(self.tileset):
                equal_perc = self.getImageEqualPercent(self.resizedTileset[tileInd], self.resizedTileset[testTileInd])
                
                is_same_dom_color, who_have_more_colors, is_colors_same_on_2_images = self.isImagesHaveColors(self.tileset[tileInd], self.tileset[testTileInd])
                # if not is_colors_same_on_2_images:
                #    continue
                if((equal_perc >= 0.60)): #0.75
                    # print(equal_perc)
                    if((self.tile_population[tileInd] < self.tile_population[testTileInd]) and who_have_more_colors and is_colors_same_on_2_images):
                        self.tileset[tileInd] = self.resizedTileset[testTileInd].resize([self.cell_size, self.cell_size], Image.NEAREST)
                    else:
                        self.tileset[testTileInd] = self.resizedTileset[testTileInd].resize([self.cell_size, self.cell_size], Image.NEAREST)
                testTileInd += 1
            tileInd += 1
        
    elif(self.similarity_method == SimilarityAlghorithm.EQUAL_PIXELS_ON_REDUCED_RESOLUTION_V2_TEST):
       #reduce every tile size
        new_res = [int(self.cell_size*threshold), int(self.cell_size*threshold)]
        if new_res[0] == 0:
           new_res = 1
        if new_res[1] == 0:
           new_res = 1
        self.resizedTileset = []
        self.resizedTileset2 = []
        self.resizedTileset3 = []
        self.resizedTileset4 = []

        for tileInd in range(len(self.tileset)):
           self.resizedTileset.append(self.tileset[tileInd].resize([new_res[0], new_res[1]], Image.NEAREST))
        for tileInd in range(len(self.tileset)):
           self.resizedTileset2.append(self.tileset[tileInd].resize([new_res[0], new_res[1]], Image.NEAREST).transpose(Image.FLIP_LEFT_RIGHT))
        for tileInd in range(len(self.tileset)):
           self.resizedTileset3.append(self.tileset[tileInd].resize([new_res[0], new_res[1]], Image.NEAREST).transpose(Image.FLIP_TOP_BOTTOM))
        for tileInd in range(len(self.tileset)):
           self.resizedTileset4.append(self.tileset[tileInd].resize([new_res[0], new_res[1]], Image.NEAREST).transpose(Image.FLIP_TOP_BOTTOM).transpose(Image.FLIP_LEFT_RIGHT))
        print("LEN:", len(self.tileset), len(self.resizedTileset))
        tileInd = 0
        testTileInd = 0

        while tileInd < len(self.tileset):
            # print(tileInd, testTileInd)
            max_equal_perc = -1
            saved_testTileInd = -1
            saved_is_same_dom_color = False
            saved_who_have_more_colors = False
            saved_is_colors_same_on_2_images = False


            while testTileInd < len(self.tileset):
               # print(testTileInd)
               equal_perc = self.getImageEqualPercent(self.resizedTileset[tileInd], self.resizedTileset[testTileInd])
               test_perc = self.getImageEqualPercent(self.resizedTileset2[tileInd], self.resizedTileset2[testTileInd])
               if test_perc > equal_perc:
                  equal_perc = test_perc
               test_perc = self.getImageEqualPercent(self.resizedTileset3[tileInd], self.resizedTileset3[testTileInd])
               if test_perc > equal_perc:
                  equal_perc = test_perc
               test_perc = self.getImageEqualPercent(self.resizedTileset4[tileInd], self.resizedTileset4[testTileInd])
               if test_perc > equal_perc:
                  equal_perc = test_perc

               is_same_dom_color, who_have_more_colors, is_colors_same_on_2_images = self.isImagesHaveColors(self.tileset[tileInd], self.tileset[testTileInd])
               if((equal_perc >= threshold) and (equal_perc > max_equal_perc) and is_same_dom_color):

                  max_equal_perc = equal_perc
                  saved_testTileInd = testTileInd
                  saved_is_same_dom_color = is_same_dom_color
                  saved_who_have_more_colors = who_have_more_colors
                  saved_is_colors_same_on_2_images = is_colors_same_on_2_images
               testTileInd += 1
               # if not is_colors_same_on_2_images:
               #    continue
               #  print("[]", testTileInd, len(self.tileset))
            # print("m: ", max_equal_perc)
            if((max_equal_perc >= 0.60) and (max_equal_perc < 1.0)): #0.75 # and is_same_dom_color
               # print((self.tile_population[tileInd], self.tile_population[saved_testTileInd]))
               if((self.tile_population[tileInd] < self.tile_population[saved_testTileInd])):
                     # and who_have_more_colors and is_colors_same_on_2_images
                     # print(testTileInd)
                     # print("1:", testTileInd, len(self.tileset))
                     # print("2:", testTileInd, len(self.resizedTileset))

                  self.tileset[tileInd] = self.resizedTileset[saved_testTileInd].resize([self.cell_size, self.cell_size], Image.NEAREST)

                  self.replaceTileIndOnTileMap(saved_testTileInd, tileInd)
                     
                  self.tileset = self.tileset[:saved_testTileInd] + self.tileset[saved_testTileInd+1:]
                  self.resizedTileset = self.resizedTileset[:saved_testTileInd] + self.resizedTileset[saved_testTileInd+1:]
                     
                  print("1a:", saved_testTileInd, len(self.tileset))
               # else:
                  
               #    self.tileset[saved_testTileInd] = self.resizedTileset[tileInd].resize([self.cell_size, self.cell_size], Image.NEAREST)
               #    self.replaceTileIndOnTileMap(saved_testTileInd, tileInd)


               #    self.tileset = self.tileset[:saved_testTileInd] + self.tileset[saved_testTileInd+1:]
               #    self.resizedTileset = self.resizedTileset[:saved_testTileInd] + self.resizedTileset[saved_testTileInd+1:]
               #    print("1b:", saved_testTileInd, tileInd, len(self.tileset))
            
            tileInd += 1
            testTileInd = tileInd +1
   #  self.tileset = self.tileset[:250]
   #  print("LLL: ", len(self.tileset))
   #  #test
   #  cols = int(self.src_img.size[0]/self.cell_size)
   #  rows = int(self.src_img.size[1]/self.cell_size)
   #  for tileY in range(rows):
   #    for tileX in range(cols):
   #       if self.tilemap[tileY][tileX] > 250:
   #          print(f"Found: {str(tileY)}")
   #          print(self.tilemap[tileY])
   #          break
    
    print("Tileset optimization is done")
  def removeIndFromArr(self, arr, removeInd):
     arr = arr[:removeInd] + arr[removeInd+1:]
     return arr
  def replaceTileIndOnTileMap(self, tileIndFrom, tileIndTo):
     img_size = self.src_img.size
     cols = int(img_size[0]/self.cell_size)
     rows = int(img_size[1]/self.cell_size)
     for tileY in range(0, rows):
       for tileX in range(0, cols):
         if self.tilemap[tileY][tileX] == tileIndFrom:
           self.tilemap[tileY][tileX] = tileIndTo
         if self.tilemap[tileY][tileX] > tileIndFrom:
            self.tilemap[tileY][tileX] = self.tilemap[tileY][tileX]-1
   
  def removeTileIndOnTileMap(self, tileIndRemove):
     img_size = self.src_img.size
     cols = int(img_size[0]/self.cell_size)
     rows = int(img_size[1]/self.cell_size)
     for tileY in range(0, rows):
       for tileX in range(0, cols):
         if self.tilemap[tileY][tileX] >= tileIndRemove:
           self.tilemap[tileY][tileX] = self.tilemap[tileY][tileX]-1


  def isImagesHaveColors(self, im1, im2):
    img_size = im1.size
    px1 = im1.load()
    px2 = im2.load()
    # equal_points = 0
    max_equal_points = img_size[0]*img_size[1]
    im1_colors = []
    im2_colors = []
    for i in range(self.src_img_amount_of_colors):
       im1_colors.append(0)
       im2_colors.append(0)
    #getting colors of img1
    for y in range(0,img_size[0]):
      for x in range(0,img_size[1]):
        im1_colors[px1[x,y]] += 1
    #getting colors of img2
    for y in range(0,img_size[0]):
      for x in range(0,img_size[1]):
        im2_colors[px2[x,y]] += 1
    
    dominant_color_index1 = 0
    dominant_color_points1 = 0
    dominant_color_index2 = 0
    dominant_color_points2 = 0

    used_colors_im1 = []
    used_colors_im2 = []
    is_colors_same_on_2_images = True

    for i in range(self.src_img_amount_of_colors):
       if im1_colors[i] != 0:
          used_colors_im1.append(i)
       if dominant_color_points1 < im1_colors[i]:
          dominant_color_index1 = i
          dominant_color_points1 = im1_colors[i]
    
    for i in range(self.src_img_amount_of_colors):
       if im2_colors[i] != 0:
          used_colors_im2.append(i)
       if dominant_color_points2 < im2_colors[i]:
          dominant_color_index2 = i
          dominant_color_points2 = im2_colors[i]

    if len(used_colors_im1) == len(used_colors_im2):
       for i in range(len(used_colors_im1)):
          if used_colors_im1[i] != used_colors_im2[i]:
             is_colors_same_on_2_images = False
             break
    else:
       is_colors_same_on_2_images = False
    who_have_more_colors = dominant_color_points1 < dominant_color_points2

    return [dominant_color_index1 == dominant_color_index2, who_have_more_colors, is_colors_same_on_2_images]
  def getImageDominantColorPercent(self, im1, im2):
    img_size = im1.size
    px1 = im1.load()
    px2 = im2.load()
    # equal_points = 0
    max_equal_points = img_size[0]*img_size[1]
    im1_colors = []
    im2_colors = []
    for i in range(self.src_img_amount_of_colors):
       im1_colors.append(0)
       im2_colors.append(0)
    #getting colors of img1
    for y in range(0,img_size[0]):
      for x in range(0,img_size[1]):
        im1_colors[px1[x,y]] += 1
    #getting colors of img2
    for y in range(0,img_size[0]):
      for x in range(0,img_size[1]):
        im2_colors[px2[x,y]] += 1
    
    dominant_color_index1 = 0
    dominant_color_points1 = 0
    dominant_color_index2 = 0
    dominant_color_points2 = 0  

    for i in range(self.src_img_amount_of_colors):
       if dominant_color_points1 < im1_colors[i]:
          dominant_color_index1 = i
          dominant_color_points1 = im1_colors[i]
    
    for i in range(self.src_img_amount_of_colors):
       if dominant_color_points2 < im2_colors[i]:
          dominant_color_index2 = i
          dominant_color_points2 = im2_colors[i]

    if(dominant_color_index1 == dominant_color_index2):
        equal_perc = dominant_color_points1/dominant_color_points2
    else:
        equal_perc = 0
    # print(equal_points, max_equal_points)
    # equal_perc = equal_points/self.src_img_amount_of_colors
    return equal_perc
  
  def getImageEqualPercent(self, im1, im2):
    img_size = im1.size
    px1 = im1.load()
    px2 = im2.load()
    equal_points = 0
    max_equal_points = img_size[0]*img_size[1]
    for y in range(0,img_size[0]):
      for x in range(0,img_size[1]):
        if(px1[x,y] == px2[x,y]):
           equal_points += 1
    # print(equal_points, max_equal_points)
    equal_perc = equal_points/max_equal_points
    return equal_perc
  def getImageEqualPercent_v2(self, im1, im2):
    img_size = im1.size
    px1 = im1.load()
    px2 = im2.load()
    equal_points = 0
    max_equal_points = img_size[0]*img_size[1]
    for y in range(0,img_size[0]):
      for x in range(0,img_size[1]):
        if(px1[x,y] == px2[x,y]):
           equal_points += 1
    # print(equal_points, max_equal_points)
    equal_perc = equal_points/max_equal_points
    return equal_perc
  def indexedPaste(self, imFrom, imTo, imToCoords = [0,0]):
    cur_img_size = imFrom.size
    pxFrom = imFrom.load()
    pxTo = imTo.load()

    for y in range(0,cur_img_size[0]):
        for x in range(0,cur_img_size[1]):
           pxTo[x + imToCoords[0], y + imToCoords[1]] = pxFrom[x, y]

    return imTo
  def recreateImageFromTilemap(self, savePath = "result.png", mode=0):
    cur_img_size = self.src_img.size
    cols = int(cur_img_size[0]/self.cell_size)
    rows = int(cur_img_size[1]/self.cell_size)
    
    imgTile1 = Image.new(mode="P", size=[self.cell_size,self.cell_size])
    #Finding used tiles on image
    for tileX in range( 0, cols):
        for tileY in range( 0, rows):
          tilePosX = tileX*self.cell_size
          tilePosY = tileY*self.cell_size
          if self.flipmap[tileY][tileX] == FlipValues.NONE:
            self.src_img.paste(self.tileset[self.tilemap[tileY][tileX]], [tilePosX, tilePosY])
          elif self.flipmap[tileY][tileX] == FlipValues.FLIP_LEFT_RIGHT:
            self.src_img.paste(self.tileset[self.tilemap[tileY][tileX]].transpose(Image.FLIP_LEFT_RIGHT), [tilePosX, tilePosY])
          elif self.flipmap[tileY][tileX] == FlipValues.FLIP_TOP_BOTTOM:
            self.src_img.paste(self.tileset[self.tilemap[tileY][tileX]].transpose(Image.FLIP_TOP_BOTTOM), [tilePosX, tilePosY])
          elif self.flipmap[tileY][tileX] == FlipValues.FLIP_TOP_BOTTOM_AND_FLIP_LEFT_RIGHT:
            self.src_img.paste(self.tileset[self.tilemap[tileY][tileX]].transpose(Image.FLIP_TOP_BOTTOM).transpose(Image.FLIP_LEFT_RIGHT), [tilePosX, tilePosY])
    
    if mode == 0:
        self.src_img.save(savePath)
  def createComparePic(self, savePath="comparePic.png", max_threshold=1.0, min_threshold=0.2, threshold_step=0.1, mode=0):
    pic_size = [0,0]
    pic_size[0] = self.src_img.size[0]
    pic_size[1] = self.src_img.size[1]

    y_step = 20

    cur_threshold = max_threshold

    compare_pic_size = [0, 0]
    compare_pic_size[0] = pic_size[0]*(int((max_threshold-min_threshold)/threshold_step)+1)
    compare_pic_size[1] = pic_size[1]+y_step
    compare_pic = Image.new("RGBA", compare_pic_size)

    draw_compare_pic = ImageDraw.Draw(compare_pic)
    posX = 0
    while cur_threshold > min_threshold:
        textPosY = 0
        self.src_img = Image.open(self.src_img_path)
        self.createTilesetFromImage()
        max_tiles = len(self.tileset)
        self.reduceTilesetSizeBySimilarity(threshold=cur_threshold)
        self.recreateImageFromTilemap(mode=1)
        self.createTilesetFromImage()
        cur_tiles = len(self.tileset)

        draw_compare_pic.text((posX, textPosY), "quality: "+str(cur_threshold)[:4])
        textPosY += 12
        draw_compare_pic.text((posX, textPosY), f"tileset len before/after: {str(cur_tiles)}/{str(max_tiles)}=" + str(cur_tiles/max_tiles)[:4] + "%")
        textPosY += 12
        draw_compare_pic.text((posX, textPosY), f"tileset len loss: " + str(1-(cur_tiles/max_tiles))[:4] + "%")
        textPosY += 12

        compare_pic.paste(self.src_img, [posX, textPosY])

        print(f"Image created with treshold: {str(cur_threshold)}")
        cur_threshold -= threshold_step
        posX += pic_size[0]
        self.src_img.close()
    compare_pic.save(savePath)

  def createTilesetFromImage(self, savePath = "tileset.png", flipTilesRemove=True):
    self.tileset = []
    cur_img_size = self.src_img.size
    cols = int(cur_img_size[0]/self.cell_size)
    rows = int(cur_img_size[1]/self.cell_size)
    
    imgTile1 = Image.new(mode="P", size=[self.cell_size,self.cell_size])
    #Finding unique tiles on image
    for tileX in range( 0, cols):
        for tileY in range( 0, rows):
            tilePosX = tileX*self.cell_size
            tilePosY = tileY*self.cell_size
            
            imgTile1 = self.src_img.crop([tilePosX, tilePosY, tilePosX+self.cell_size, tilePosY+self.cell_size])
            pass_step = False
            #If tile aready exists in tileset
            for i in range(len(self.tileset)):
               if imgTile1 == self.tileset[i]:
                  pass_step = True
                  self.tile_population[i] += 1
                  self.tilemap[tileY][tileX] = i
                  self.flipmap[tileY][tileX] = FlipValues.NONE
                  break
               if flipTilesRemove:
                 if imgTile1.transpose(Image.FLIP_LEFT_RIGHT) == self.tileset[i]:
                    pass_step = True
                    self.tile_population[i] += 1
                    self.tilemap[tileY][tileX] = i
                    self.flipmap[tileY][tileX] = FlipValues.FLIP_LEFT_RIGHT
                    break
                 elif imgTile1.transpose(Image.FLIP_TOP_BOTTOM) == self.tileset[i]:
                    pass_step = True
                    self.tile_population[i] += 1
                    self.tilemap[tileY][tileX] = i
                    self.flipmap[tileY][tileX] = FlipValues.FLIP_TOP_BOTTOM
                    break
                 elif imgTile1.transpose(Image.FLIP_TOP_BOTTOM).transpose(Image.FLIP_LEFT_RIGHT) == self.tileset[i]:
                    pass_step = True
                    self.tile_population[i] += 1
                    self.tilemap[tileY][tileX] = i
                    self.flipmap[tileY][tileX] = FlipValues.FLIP_TOP_BOTTOM_AND_FLIP_LEFT_RIGHT
                    break
            #Then, not adding this tile in tileset
            if pass_step:
               continue
            #Add new tile in tilesey
            self.tileset.append(imgTile1)
            
            # print(tileX, tileY)
            #Updating tilemap
            self.tilemap[tileY][tileX] = len(self.tileset)-1

            
            #Update tile population  
            self.tile_population.append(1)   

    #Remove filpped tiles
    
    # imgTile1.close()
    #generate tileset image
    tileset_img = Image.new(mode="P", size=[len(self.tileset)*self.cell_size, self.cell_size])
    tileset_img.putpalette(self.src_img_pal)
    for tileX in range(0, len(self.tileset)):
      self.indexedPaste(self.tileset[tileX], tileset_img, (tileX*self.cell_size,0))
    print(f"Generated tileset which contains [{str(len(self.tileset))}] unique tiles")
    tileset_img.save(savePath)

def use_example():
   reducer = uniqueTileReducer(src_img_path="map.png", sim_method=SimilarityAlghorithm.EQUAL_PIXELS_ON_REDUCED_RESOLUTION_V2)
   reducer.createTilesetFromImage()
   print(len(reducer.tileset))
   reducer.reduceTilesetSizeBySimilarity(0.4) # val from 0.2 to 1.0, the less value, the less detailed image, the less unique tiles
   reducer.recreateImageFromTilemap()
   reducer.createTilesetFromImage()
   print(len(reducer.tileset))

def use_example_2():
   reducer = uniqueTileReducer(src_img_path="map.png", sim_method=SimilarityAlghorithm.EQUAL_PIXELS_ON_REDUCED_RESOLUTION_V2)
   reducer.createComparePic(savePath="compareExample.png",min_threshold=0.2)


use_example_2()