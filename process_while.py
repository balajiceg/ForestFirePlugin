import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from osgeo import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
import numpy as np
import gdal
from osgeo.gdalconst import *
import math
import os,subprocess
from scipy import ndimage,stats
import matplotlib.pyplot as plt
psth= r'C:\Users\Idiot\Desktop\ffmp\bin\ffmpeg.exe'
plt.rcParams['animation.ffmpeg_path'] =psth.decode("utf-8")
#########globals
number_band=1
no_data=-999

sys.setrecursionlimit(10000)
np.set_printoptions(threshold=np.inf)


def reclass(arr,rev=False,classes=100):
    classes=classes+2
    max=np.amax(arr)
    tmp=np.copy(arr)
    tmp[tmp==0]=max+1
    min=np.amin(tmp)
    del tmp
    intervals=np.linspace(min,max,classes)
    classified=np.ones(arr.shape, dtype=int)
    add=0
    if rev:
        add=classes-1
    for counter, value in enumerate(intervals):
        if counter<len(intervals)-1:
            classified[np.logical_and(arr>=value,arr<intervals[counter+1])]=abs(add-(counter+1))
    #print (min,max)
    #print np.amax(classified)
    #print np.amin(classified)
    return classified
    
    

def read_data(filename):
    fileInfo = QFileInfo(filename)
    baseName = fileInfo.baseName()
    layer = QgsRasterLayer(filename, baseName)
    if not layer.isValid():
        print(filename+" layer failed to load!")
    ds = gdal.Open(filename)
    proj = ds.GetProjection()
    geotransform = ds.GetGeoTransform()
    band = ds.GetRasterBand(1)
    no_dat= band.GetNoDataValue()
    array = np.array(band.ReadAsArray())
    XSize,YSize=(band.XSize,band.YSize)
    return array,no_dat,proj,geotransform,XSize,YSize 

def latlngToPix(mx,my,gt):#gt:geotransform param
    col = int((mx - gt[0]) / gt[1])
    row = int((my - gt[3]) / gt[5])
    return (row,col)
    




'''
def burncell(i,j,val):
    global new,ulti_array,wind_array,XSize,YSize,no_data1,imax,jmax
    ##print val
    if np.isnan(new[i][j]) :
        new[i][j]=val
        ulti_array[i][j]=no_data1

    
    if new[i][j]==-1 or new[i][j]==np.float32(-1):
        #print "new less than 0"
        return
        
    if val>=steps:
        #print "steps over"
        return
    
    if(i>=imax or i<1 or j>=jmax or j<1):
        #print "border"
        return
  
    neigh=np.copy(ulti_array[i-1:i+2,j-1:j+2])
    neigh[1][1]=no_data1
    
    if np.unique(neigh).size==1 and np.unique(neigh)[0]==no_data1 :
        #print "all burnt"
        return
   
    mul_f=1.45
    ####################################
    w=wind_array[i][j].item()
    
    if((w>=316.0) or (w>-0.1 and w<=44.00)):
        neigh[0][1]*=mul_f
    elif(w>44.0 and w<46.0):
        neigh[0][2]*=mul_f
    elif(w>=46.0 and w<=134.0):
        neigh[1][2]*=mul_f
    elif(w>134.0 and w<136.0):
        neigh[2][2]*=mul_f
    elif(w>=136.0 and w<=224.0):
        neigh[2][1]*=mul_f
    elif(w>224.0 and w<250.0):
        neigh[2][0]*=mul_f
    elif(w>=250.0 and w<=314.0):
        neigh[1][0]*=mul_f
    elif(w>314.0 and w<316.0):
        neigh[0][0]*=mul_f

    ####################################
    if neigh.max()<0.0000 :
        #print neigh.max()
        return

    indices=np.where(neigh == neigh.max())
    x=indices[0][0]
    y=indices[1][0] 
    burncell((i-1)+x,(j-1)+y,val+1)
    burncell(i,j,val+1)
    ##print(val,"------------------------------")
'''
####################


# dem_file=r"C:\Users\Idiot\Desktop\mp\final\elevation.tif"
# green_file=r"C:\Users\Idiot\Desktop\mp\final\green_ref.tif"
# red_file=r"C:\Users\Idiot\Desktop\mp\final\red_ref.tif"
# nir_file=r"C:\Users\Idiot\Desktop\mp\final\nir_ref.tif"
# swir_file=r"C:\Users\Idiot\Desktop\mp\final\swir1_ref.tif"
wind=r"C:\Users\Idiot\Desktop\mp\final\wind_final.tif"

# output_dir=r"C:\Users\Idiot\Desktop\mp\final\output"
# NDVI=0.25

def run_code(dem_file,green_file,red_file,nir_file,swir_file,output_dir,NDVI,progdialog,time_step,shape_file,burnt_file):
    #global new,ulti_array,wind_array,XSize,YSize,no_data1,imax,jmax,steps
    no_data=-999
    
    steps=time_step
    progdialog.setValue(5)
    progdialog.setLabelText("reading rasters...")   
    progdialog.setAutoClose(False)
   
    windp=r"C:\Users\Idiot\Desktop\mp\final\wind_final.tif"

   
   #reading raster
    dem = read_data(dem_file)[0]
    green = read_data(green_file)[0]
    nir = read_data(nir_file)[0]
    red=read_data(red_file)[0]
    swir= read_data(swir_file)[0]
    wind=read_data(windp)[0]
    ground_truth=read_data(burnt_file)[0]
    
    
    geotransform=read_data(nir_file)[3]
    XSize=read_data(windp)[4]
    YSize=read_data(windp)[5]
    
    progdialog.setValue(10)
    progdialog.setLabelText("Creating Mask...")
    
    
    #creating slope
    subprocess.call(["gdaldem", "slope",dem_file,output_dir+r"\slope.tif","-b","1","-s","1","-of","GTiff","-compute_edges"])
    slope=read_data(output_dir+r"\slope.tif")[0]
    subprocess.call(["gdaldem", "aspect",dem_file,output_dir+r"\aspect.tif","-b","1","-of","GTiff","-compute_edges"])
    aspect=read_data(output_dir+r"\aspect.tif")[0]
    #creating mask
    ndvi=((nir-red)/(nir+red))
    ndvi_l=ndvi>NDVI 
    ndwi=(green-nir)/(green+nir)
    mndwi=(green-swir)/(green+swir)
    ndwi_p_mndwi=(ndwi+mndwi)>0
    mask=np.logical_and(np.logical_not(ndwi_p_mndwi),ndvi_l)
    mask=np.uint8(mask)
    del ndwi,ndvi_l,ndwi_p_mndwi
    #sleving for largest water body
    #grouping [pixels]

    # b=np.ones(shape=[3,3],dtype=np.uint8);
    # mask, num_features = ndimage.measurements.label(mask,b)
    # unique, counts = np.unique(mask, return_counts=True)
    # #deleting no data counts
    # unique=np.delete(unique,0)
    # counts=np.delete(counts,0)
    # #find largest group
    # pos=np.argmax(counts)
    # mask[mask!=unique[pos]] =0
    # mask[mask!=0]=1
    # mask=np.uint8(mask)

    #masking the required bands
    slope=mask*slope
    mndfi=mask*mndwi
    aspect=mask*aspect
    ndvi=mask*ndvi
    
    #overlaying
    weight=reclass(ndvi,True)+reclass(slope)*2+reclass(mndfi,True)*2
    
    possi_array=np.float32(weight)*mask
    ulti_array=np.copy(possi_array)
    wind_array=np.float32(wind)*mask
    
###############################################################shape file
    progdialog.setValue(34)
    progdialog.setLabelText("Reading shape file...")
    #read shape file and getdata
    vlayer = QgsVectorLayer(shape_file, "points", "ogr")
    fea=vlayer.getFeatures()
    J=[]
    I=[]
  
    for feat in fea:
        geom = feat.geometry()
        p = geom.asPoint()
        
        row,col=latlngToPix(p[0],p[1],geotransform)
        if(row>=0 and col>=0 and row<ulti_array.shape[0] and col<ulti_array.shape[1]):
            if(~np.isnan(ulti_array[row,col])):
                J.append(col)
                I.append(row)
                #rel_z_red.append(rel_depth_red[x,y])
################################################################        
    progdialog.setValue(40)
    progdialog.setLabelText("Running main Algorithm....")
    #read shape file and getdata
    no_data=np.float32(no_data)

    new = np.zeros(shape=(YSize,XSize),dtype=np.float32)
    new.fill(0)

    
    new[(ulti_array==np.float32(0))]=no_data

    imax=YSize-1
    jmax=XSize-1

    presnt_burnig=list(zip(I,J))
    for i,j in presnt_burnig:
        new[i][j]=1
        ulti_array[i][j]=no_data
    step=2
    all_burning=presnt_burnig[:]
    while all_burning and step<=steps:
        presnt_burnig=[]
        list_i=0
        while list_i<len(all_burning):
            i,j = all_burning[list_i]
            
            neigh=np.copy(ulti_array[i-1:i+2,j-1:j+2])
            neigh[1][1]=no_data
            if np.unique(neigh).size==1 and np.unique(neigh)[0]==no_data :
                all_burning.pop(list_i)
                continue
            # mul_f=1.45
            mul_f=2
            ####################################
            w=wind_array[i][j].item()
            
            if((w>=316.0) or (w>-0.1 and w<=44.00)):
                neigh[0][1]*=mul_f
            elif(w>44.0 and w<46.0):
                neigh[0][2]*=mul_f
            elif(w>=46.0 and w<=134.0):
                neigh[1][2]*=mul_f
            elif(w>134.0 and w<136.0):
                neigh[2][2]*=mul_f
            elif(w>=136.0 and w<=224.0):
                neigh[2][1]*=mul_f
            elif(w>224.0 and w<250.0):
                neigh[2][0]*=mul_f
            elif(w>=250.0 and w<=314.0):
                neigh[1][0]*=mul_f
            elif(w>314.0 and w<316.0):
                neigh[0][0]*=mul_f

            ####################################
            if neigh.max()<=0.0000 :
                all_burning.pop(list_i)
                continue
                
            indices=np.where(neigh == neigh.max())
            x=indices[0][0]
            y=indices[1][0] 
            
            presnt_burnig.append([(i-1)+x,(j-1)+y])
            ulti_array[(i-1)+x][(j-1)+y]=no_data
            new[(i-1)+x][(j-1)+y]=step
            
            list_i+=1
            ####     
        all_burning=all_burning+presnt_burnig   
        step=step+1
        print(step)
        
    
    
    #removing layer from canvas
    if len(QgsMapLayerRegistry.instance().mapLayers().values())>0:
        for v in QgsMapLayerRegistry.instance().mapLayers().values():
            if (v.id().find('time')!=-1 or v.id().find('mask')!=-1 or v.id().find('relative')!=-1):
                QgsMapLayerRegistry.instance().removeMapLayer(v.id())
                
                
    ##getting input raster data to set transformations
    _,_,proj,geotransform,XSize,YSize =read_data(green_file)


    progdialog.setValue(90)
    progdialog.setLabelText("Creating output files...")
    ##creating mask raster
    output_file = output_dir+r"\mask.tif"
    driver = gdal.GetDriverByName("GTiff")
    dst_ds = driver.Create(output_file, 
                           XSize, 
                           YSize, 
                           number_band, 
                           GDT_Byte)
    #writting mask raster
    dst_ds.GetRasterBand(number_band).WriteArray(mask)
    #set no data value
    dst_ds.GetRasterBand(number_band).SetNoDataValue(-1)
    #setting extension of mask raster
    # top left x, w-e pixel resolution, rotation, top left y, rotation, n-s pixel resolution
    dst_ds.SetGeoTransform(geotransform)
    # setting spatial reference of mask raster 
    srs = osr.SpatialReference(wkt = proj)
    dst_ds.SetProjection( srs.ExportToWkt() )
    del dst_ds



    # #creating relative depth raster
    # output_file1 = output_dir+r"\relative_depth.tif"
    # driver = gdal.GetDriverByName("GTiff")
    # dst_ds = driver.Create(output_file1, 
                           # XSize, 
                           # YSize, 
                           # number_band, 
                           # GDT_Float64)
    # #writting relative depth raster
    # dst_ds.GetRasterBand(number_band).WriteArray(rel_depth )
    # #set no data value
    # dst_ds.GetRasterBand(number_band).SetNoDataValue(no_data)
    # #setting extension of relative depth raster
    # # top left x, w-e pixel resolution, rotation, top left y, rotation, n-s pixel resolution
    # dst_ds.SetGeoTransform(geotransform)
    # # setting spatial reference of relative depth raster 
    # srs = osr.SpatialReference(wkt = proj)
    # dst_ds.SetProjection( srs.ExportToWkt() )






    ##creating output raster
    output_file2 = output_dir+r"\time.tif"
    driver = gdal.GetDriverByName("GTiff")
    dst_ds = driver.Create(output_file2, 
                           XSize, 
                           YSize, 
                           number_band, 
                           GDT_Float32)
    #writting output raster
    dst_ds.GetRasterBand(number_band).WriteArray(new)
    #set no data value
    dst_ds.GetRasterBand(number_band).SetNoDataValue(int(no_data))
    #setting extension of output raster
    # top left x, w-e pixel resolution, rotation, top left y, rotation, n-s pixel resolution
    dst_ds.SetGeoTransform(geotransform)
    # setting spatial reference of output raster 
    srs = osr.SpatialReference(wkt = proj)
    dst_ds.SetProjection( srs.ExportToWkt() )
    del dst_ds

    
    # #Close output raster dataset 
    # del dst_ds,green,blue,rel_depth,driver
    
    progdialog.setValue(80)
    progdialog.setLabelText("Adding outputs to canvas...")
    #display the output
    _=iface.addRasterLayer(output_file, "mask")
    # _=iface.addRasterLayer(output_file1, "relative depth")
    layer=iface.addRasterLayer(output_file2, "time")
    
    
    fcn = QgsColorRampShader()
    fcn.setColorRampType(QgsColorRampShader.INTERPOLATED)
    mmax=np.nanmax(new)
    mmin=1
    #print mmax
    
    color_list=[ QColor(0,0,0),QColor(247, 255, 20),QColor(141, 255, 20),QColor(8, 201, 82),QColor(6, 232, 232),QColor(6, 122, 232),QColor(17, 6, 232),\
    QColor(126, 6, 232),QColor(216, 6, 232),QColor(201, 4, 119),QColor(226, 6, 6)]
    lst=[]
    tot=mmin
    for i in range(len(color_list)):
        lst.append( QgsColorRampShader.ColorRampItem(tot,color_list[i]))
        tot=tot+(mmax-mmin)/len(color_list)
    
    
    
    fcn.setColorRampItemList(lst)
    shader = QgsRasterShader()
    shader.setRasterShaderFunction(fcn)
    renderer = QgsSingleBandPseudoColorRenderer(layer.dataProvider(), 1, shader)
    renderer.setClassificationMax(mmax)
    renderer.setClassificationMin(mmin)

    ce = QgsContrastEnhancement(layer.dataProvider().dataType(0))
    ce.setContrastEnhancementAlgorithm(QgsContrastEnhancement.StretchToMinimumMaximum)
    ce.setMinimumValue(1)
    ce.setMaximumValue(mmax)
    renderer.setContrastEnhancement(ce)

    layer.setRenderer(renderer)

 

    #preparing animation
    progdialog.setValue(90)
    progdialog.setLabelText("Preparing animation...")
    

    max=np.nanmax(new)
    x,y=np.where(new==max)
    x_min=np.amin(x)
    x_max=np.amax(x)
    y_min=np.amin(y)
    y_max=np.amax(y)
    d=new[x_min:x_max,y_min:y_max]
    d=np.array(d)

    img=np.copy(d)
    img[img>0]=0
    fig = plt.figure()
    ims = []

    for i in range(0,int(max+1),2):
        img[d<i]=0.865
        img[d<0]=-1
        im = plt.imshow(img, animated=True)
        im.set_cmap('nipy_spectral')
        ims.append([im])

    ani = animation.ArtistAnimation(fig, ims, interval=3, blit=True,repeat_delay=1000)
    ani.save(output_dir+r"\Burning.mp4")
    #plt.show()
    '''
    ############################################################
   #performing accuracy assesment
    ground_truth=np.array(ground_truth,dtype=np.float32)
    ground_truth[np.isnan(ground_truth)]=0
    ground_truth[ground_truth>=255]=0
    ground_truth[ground_truth>0]=10
    ground_truth[ground_truth<=0]=0
    
    
    

    new[np.isnan(new)]=0
    new[new>0]=20
    new[new<=0]=0
    

    error=new-ground_truth
    correct=np.count_nonzero(error==np.float32(20-10))
    wrong=np.count_nonzero(error!=np.float32(20-10))
    wrong=wrong-np.count_nonzero(error==np.float32(0))
    
    
    i=correct*100.00/(correct+wrong)
    accuracy=i
    print correct,wrong

    fig2=plt.figure()
    im = plt.imshow(error)

    plt.show()
    '''
    #print "completed"
    progdialog.setValue(101)
    
    #progdialog.setLabelText("Completed. Accuracy= "+str(i))
    progdialog.setCancelButtonText('Ok')
    #print new[0][0]
#run_code(blue_file,green_file,meta_file,output_dir,None)

