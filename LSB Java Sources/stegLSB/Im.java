package stegLSB;

import java.awt.Point;
import java.awt.Transparency;
import java.awt.color.ColorSpace;
import java.awt.image.BufferedImage;
import java.awt.image.ColorModel;
import java.awt.image.ComponentColorModel;
import java.awt.image.DataBuffer;
import java.awt.image.DataBufferByte;
import java.awt.image.Raster;
import java.awt.image.WritableRaster;
import java.io.File;
import java.io.IOException;
import java.util.Arrays;
import java.util.BitSet;

import javax.imageio.ImageIO;



public abstract class Im {

	static int[] pixelIndexToCoords(int n, int w) {
		int[] res = new int[2];
		res[0] = n % w;
		res[1] = n / w;
		return res;
	}
	
	static int coordsToPixelIndex(int x, int y, int w) {
		return w*y + x;
	}
	
	static int[] byteIndexToCoords(int n, int w, int bpp) {
		return pixelIndexToCoords(n/bpp, w);
	}
	
	static int coordsToByteIndex(int x, int y, int w, int bpp) {
		return coordsToPixelIndex(x,y,w)*bpp;
	}
	
	static byte[] extractFlatBytes(BufferedImage pic, int start, int stop) {
		//Extract the *bytes* numbered between start and stop, inclusive. This may or may not be 1 byte per pixel, so there is conversion to be done
		
		int bytesPerPixel = pic.getColorModel().getNumComponents();
		
		int imW = pic.getWidth();
		int imH = pic.getHeight();
		
		int[] coordsStart = byteIndexToCoords(start, imW, bytesPerPixel);
		int[] coordsStop = {imW-1,imH-1};
		
		if(stop >= 0) {
			coordsStop = byteIndexToCoords(stop,imW, bytesPerPixel);
		}
		
		
		int h = coordsStop[1]-coordsStart[1]+1;
		byte[] out =  (byte[]) pic.getRaster().getDataElements(0,coordsStart[1],imW,h, null);
		int startIndex = start % (imW*bytesPerPixel);
		

		if(stop >= 0) {
			return Arrays.copyOfRange(out, startIndex, stop-start+startIndex+1);
		} else {
			return out;
		}
	}
	
	static byte[] merge(byte[] input, BitSet header, BitSet body, int offset) {
		byte[] imageBytes = new byte[input.length];
		java.lang.System.arraycopy(input, 0, imageBytes, 0, input.length);
		
		for(int i=0; i < 80; i++) {//Header size = 83
			 imageBytes[i] = (byte) (imageBytes[i] & 254);
			 imageBytes[i] = (byte) (imageBytes[i] | (header.get(i) ? 1 : 0));
		}
		
		for(int i = offset; i < offset+body.length()-1; i++) {
			imageBytes[i] = (byte) (imageBytes[i] & 254);
			imageBytes[i] = (byte) (imageBytes[i] | ((body.get(i-offset) ? 1 : 0)));
		}
		
		return imageBytes;
		
	}
	
	static void createImage(String path, byte[] data, int w, int h, int mode) throws IOException {
		DataBuffer buffer = new DataBufferByte(data, data.length);
		WritableRaster raster = null;
		ColorModel cm = null;
		
		if(mode == 0) { //Monochrome
			raster = Raster.createInterleavedRaster(buffer, w, h, w, 1, new int[] {0}, (Point)null);
			cm = new ComponentColorModel(ColorSpace.getInstance(ColorSpace.CS_GRAY), false, true, Transparency.OPAQUE, DataBuffer.TYPE_BYTE);
		} else if(mode == 1) { //RGB
			raster = Raster.createInterleavedRaster(buffer, w, h, 3 * w, 3, new int[] {0, 1, 2}, (Point)null);
			cm = new ComponentColorModel(ColorModel.getRGBdefault().getColorSpace(), false, true, Transparency.OPAQUE, DataBuffer.TYPE_BYTE);
		}

		BufferedImage image = new BufferedImage(cm, raster, true, null);
		
		ImageIO.write(image, "png", new File(path));
	}
}
