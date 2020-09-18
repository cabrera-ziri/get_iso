import urllib
import tempfile
import zipfile
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from shutil import copyfile

def get_iso(logage,fe,phot,ofile,Av=0):
    """Download the synthetic photometry for a 
    MIST isochrone of a given logage and [Fe/H].
    
    Filter options:
    
        'CFHT/MegaCam'
        'DECam'
        'HST ACS/HRC'
        'HST ACS/WFC'
        'HST WFC3/UVIS+IR'
        'HST WFPC2'
        'INT / IPHAS'
        'GALEX'
        'JWST'
        'LSST'
        'PanSTARRS'
        'SDSS'
        'SkyMapper'
        'Spitzer IRAC'
        'Subaru Hyper Suprime-Cam'
        'Swift'
        'UBV(RI)c + 2MASS + Kepler + Hipparcos + Gaia'
        'UKIDSS'
        'VISTA'
        'Washington + Strömgren + DDO51'
        'WFIRST (preliminary)'
        'WISE'
    """
    if not (5<= logage) or not (logage <= 10.3):
        return print('The available range is 5 ≤ log(Age[yr]) ≤ 10.3')

    if not (-4<= fe) or not (fe <= 0.5):
        return print('The available range is -4 ≤ [Fe/H] ≤ +0.5')
    
    # open interwebs
    driver = webdriver.Firefox()

    # load mist website
    website = 'https://waps.cfa.harvard.edu/MIST/interp_isos.html'
    driver.get(website)

    # select single age
    single_age = '/html/body/div[1]/div[2]/div/div/article/div/form/fieldset[1]/input[3]'

    single_age_select = driver.find_element_by_xpath(single_age)
    single_age_select.click()

    # type in age in box
    age_box = '/html/body/div[1]/div[2]/div/div/article/div/form/fieldset[1]/input[4]'
    age_box = driver.find_element_by_xpath(age_box)

    age_box.clear()
    age_box.send_keys('{:}'.format(logage))

    # type in fe in box
    fe_box = '/html/body/div[1]/div[2]/div/div/article/div/form/fieldset[2]/input'
    fe_box = driver.find_element_by_xpath(fe_box)

    fe_box.clear()
    fe_box.send_keys('{:}'.format(fe))

    # type in Av box
    av_box = '/html/body/div[1]/div[2]/div/div/article/div/form/fieldset[3]/input[3]'
    av_box = driver.find_element_by_xpath(av_box)

    av_box.clear()
    av_box.send_keys('{:}'.format(Av))
    
    # select synthetic photometry
    synth_phot = '/html/body/div[1]/div[2]/div/div/article/div/form/fieldset[3]/input[2]'

    synth_phot_select = driver.find_element_by_xpath(synth_phot)
    synth_phot_select.click()

    # pick a set of filters
    filters = '/html/body/div[1]/div[2]/div/div/article/div/form/fieldset[3]/select[2]'

    filter_element = driver.find_element_by_xpath(filters)
    
    phot_select = False # flag in case of phot is not found
    
    for option in filter_element.find_elements_by_tag_name('option'):
        if option.text == phot:
            option.click() # select() in earlier versions of webdriver
            phot_select = True
            break
    if not phot_select:
        driver.close()
        return print('{:} is not in the synthetic photometry options.\nSee doc for available options.'.format(phot))
        
    # click on generate isochrone
    gen_iso = '/html/body/div[1]/div[2]/div/div/article/div/form/button'

    generate = driver.find_element_by_xpath(gen_iso)
    generate.click()

    # A new window will open with the link
    timeout = 30 #sec

    href = WebDriverWait(driver, timeout).until(lambda x: x.find_element_by_link_text('Click here for Synthetic CMDs'))
    iso = href.get_attribute('href')

    # prepare to download file
    # urllib.request.urlretrieve(iso,filename=ofile)
    zipfname = iso.split('/')[-1]

    # Create tmpdir for download
    with tempfile.TemporaryDirectory() as tmpdirname:
#         print('created temporary directory', tmpdirname)
        zippath = tmpdirname+'/'+zipfname

    #     download file to tmp dir
        urllib.request.urlretrieve(iso,filename=zippath)

    #     unzip
        with zipfile.ZipFile(zippath, 'r') as zip_ref:
            zip_ref.extract(zipfname.replace('zip','cmd'),path=tmpdirname)

    #     copy file to ofile
        copyfile(tmpdirname+'/'+zipfname.replace('zip','cmd'), ofile)

    driver.close()
    
    return print('{:} isochrone with logage:{:.3f}, [Fe/H]:{:.3f} and Av:{:.3f} saved in: {:}'.format(phot,logage,fe,Av,ofile))
