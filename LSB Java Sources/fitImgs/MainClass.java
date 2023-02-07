package fitImgs;

import java.awt.Image;
import java.awt.Toolkit;
import java.awt.image.BufferedImage;
import java.awt.image.ColorConvertOp;
import java.awt.image.FilteredImageSource;
import java.awt.image.ImageFilter;
import java.awt.image.ImageProducer;
import java.io.File;
import java.io.FilenameFilter;
import java.io.IOException;

import javax.imageio.ImageIO;
import javax.swing.GrayFilter;

public class MainClass {

	static BufferedImage resizeImage(BufferedImage originalImage, int targetWidth, int targetHeight) throws IOException {
	    Image resultingImage = originalImage.getScaledInstance(targetWidth, targetHeight, Image.SCALE_DEFAULT);
	    BufferedImage outputImage = new BufferedImage(targetWidth, targetHeight, BufferedImage.TYPE_INT_RGB);
	    outputImage.getGraphics().drawImage(resultingImage, 0, 0, null);
	    return outputImage;
	}
	
	
	public static void main(String[] args) throws IOException {
		FilenameFilter filter = new FilenameFilter() {
			public boolean accept(File dir, String name) {
	            String lowercaseName = name.toLowerCase();
	            if (lowercaseName.endsWith(".png") || lowercaseName.endsWith(".jpg")) {
	               return true;
	            } else {
	               return false;
	            }
	         }
		};
		
		String imagesPath = "Z:\\Boulot\\TIPE\\BDD\\Stego App DB\\ORIGINAL - All Devices, JPG, .9, Auto\\originals\\Sub 2";
		String outputPath = "Z:\\Boulot\\TIPE\\BDD\\Resized Grayscales";
		String id = "SADB2";
		String[] imgNames = new File(imagesPath).list(filter);
		
		int done = 0;
		
		for(String s:imgNames) {
			BufferedImage img = ImageIO.read(new File(imagesPath+"\\"+s));
			
			BufferedImage newImage = resizeImage(img, 512, 512);
			
			BufferedImage finalImage = new BufferedImage(newImage.getWidth(), newImage.getHeight(), BufferedImage.TYPE_BYTE_GRAY );  
			ColorConvertOp op = new ColorConvertOp( newImage.getColorModel().getColorSpace(), finalImage.getColorModel().getColorSpace(), null );
			op.filter( newImage, finalImage );
			
			ImageIO.write(finalImage, "png", new File(outputPath+"\\"+id+"_"+s));
			done++;
			System.out.println("Processed "+String.valueOf(done)+" out of "+String.valueOf(imgNames.length)+" images.");

		}
	}

}
