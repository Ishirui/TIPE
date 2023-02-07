package stegLSB;
import java.awt.image.BufferedImage;
import java.awt.image.ColorModel;
import java.io.File;
import java.io.FilenameFilter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.Arrays;
import java.util.BitSet;
import java.util.Collections;
import java.util.List;
import java.util.Random;

import javax.imageio.ImageIO;



public class MainClass {

	static String defaultTextPath = "C:\\Users\\pierr\\Documents\\TIPE\\shakespeare_allcombined.txt";
	static byte[] defaultTextData = By.getFileData(defaultTextPath);
	static int defaultTextSize = defaultTextData.length;
	static int minEmbedSize = 100; //In bytes
	static int maxEmbedSize = 1000; //In bytes
	
	public static void printBitSet(BitSet input) {
		for(int i = 0; i < input.length(); i++) {
			System.out.print(input.get(i)? '1':'0');
		}
		System.out.println();
	}
	
	public static void printByteArray(byte[] input) {
		for(byte b: input) {
			System.out.println(Integer.toBinaryString((b & 0xFF) + 0x100).substring(1));
		}
		System.out.println();
	}
	
	static void extractLSBs(String imagePath, String outputPath) throws IOException {
		BufferedImage img = ImageIO.read(new File(imagePath)); 
		
		byte[] rawImageBytes = Im.extractFlatBytes(img, 0, -1);
		BitSet LSB = By.getLSBs(rawImageBytes);
		byte[] newImageBytes = new byte[rawImageBytes.length];
		for(int i = 0; i < rawImageBytes.length; i++) {
			newImageBytes[i] = (LSB.get(i))?(byte)0xFF:(byte)0x00;
		}
		int mode = (img.getColorModel().getColorSpace() == ColorModel.getRGBdefault().getColorSpace())? 1 : 0;
		Im.createImage(outputPath, newImageBytes, img.getWidth(), img.getHeight(), mode);
	}

	
	public static void encode(String imagePathString, String fileName, String outputFolderString, byte[] fileData, int offset, boolean LSBs) throws IOException {
		String imageName = Paths.get(imagePathString).getFileName().toString();
		
		BufferedImage rawImage = ImageIO.read(new File(imagePathString));
		
		BitSet header = By.getHeader(offset, fileName.length()*8, fileData.length*8);
		BitSet body = By.getBody(fileName, fileData);
		
		byte[] rawImageBytes = Im.extractFlatBytes(rawImage, 0, -1);
		
		byte[] newImageBytes = Im.merge(rawImageBytes, header, body, offset);
		int mode = (rawImage.getColorModel().getColorSpace() == ColorModel.getRGBdefault().getColorSpace())? 1 : 0;
		
		if(LSBs) {
			BitSet LSB = By.getLSBs(newImageBytes);
			newImageBytes = new byte[rawImageBytes.length];
			for(int i = 0; i < rawImageBytes.length; i++) {
				newImageBytes[i] = (LSB.get(i))?(byte)0xFF:(byte)0x00;
			}
		}
		
		
		Im.createImage(outputFolderString+"\\stegged_"+imageName, newImageBytes, rawImage.getWidth(), rawImage.getHeight(), mode);
	}
	
	public static void decode(String imagePathString, String outputFolderString) throws IOException {
		BufferedImage img = ImageIO.read(new File(imagePathString));
		
		
		int offset = By.asNum(By.getLSBs(Im.extractFlatBytes(img, 0, 31))); //Etc, see getHeader
		int fileNameSize = By.asNum(By.getLSBs(Im.extractFlatBytes(img, 32, 47)));
		int fileSize = By.asNum(By.getLSBs(Im.extractFlatBytes(img, 48, 79)));
		
		
		int pointer = offset;
		
		BitSet fileNameBits = By.getLSBs(Im.extractFlatBytes(img, pointer, pointer+=(fileNameSize-1)));
		BitSet fileBits = By.getLSBs(Im.extractFlatBytes(img, pointer+1, pointer+1+fileSize));
		
		

		String fileName = new String(fileNameBits.toByteArray(), StandardCharsets.UTF_8);
		byte[] fileData = fileBits.toByteArray();
		
		fileData = Arrays.copyOfRange(fileData, 0, fileSize/8);

		By.writeFile(outputFolderString+"\\"+fileName, fileData);
	}
	
	public static void createSteg(String imagePath, String outputFolderPath, String encode, boolean LSBs) throws IOException {
		BufferedImage img = ImageIO.read(new File(imagePath));
		int capacity = img.getWidth()*img.getHeight()*img.getColorModel().getNumComponents()-80; //In bits, excluding the header
		
		byte[] output;
		String fileName;
		
		if(encode.equals("text") || encode.equals("random")) {
			int embedSize = new Random().nextInt(maxEmbedSize-minEmbedSize)+minEmbedSize;
			output = new byte[embedSize];
			if(encode.equals("text")) {
				System.arraycopy(defaultTextData, new Random().nextInt(defaultTextSize-embedSize-1), output, 0, embedSize);
				fileName = "randTxt.txt";
			} else {
				new Random().nextBytes(output);
				fileName = "randBytes";
			}
		} else {
			output = By.getFileData(encode);
			fileName = Paths.get(encode).getFileName().toString();
		}
		
		int offset = 81 + new Random().nextInt(capacity-output.length*8);
		
		encode(imagePath, fileName, outputFolderPath, output, offset, LSBs);
	}

	public static void main(String[] args) throws IOException {
		//args[0] = mode -- encode, decode, batchEncode, batchDecode, prepareDataset
		//args[1] = inputPath, either the image file itself or imageFile directory
		//args[2] = outputFolderPath, output directory
		//args[3] = encodeMode, a file path for encoding a single file, "text" for random text extracted from the specified file, "random" for random bytes
		//args[4] = LSBs, flag whether to pre-extract the LSBs
		//args[5] = percentages of each set to make (train, valid, test)
		//args[6] = percentage of stego images
		
		String mode = args[0];
		String inputPath = args[1];
		String outputFolderPath = args[2];
		boolean LSBs;
		
		if(args.length >= 5) {
			LSBs = (args[4].equals("true"));
		}else {
			LSBs = false;
		}
		
		FilenameFilter filter = new FilenameFilter() {
			public boolean accept(File dir, String name) {
	            String lowercaseName = name.toLowerCase();
	            if (lowercaseName.endsWith(".png")) {
	               return true;
	            } else {
	               return false;
	            }
	         }
		};
		
		
		switch(mode) {
			case "encode":
				createSteg(inputPath, outputFolderPath, args[3], LSBs);
				break;
			case "batchEncode":
				String[] images = new File(inputPath).list(filter);
				int i = 0;
				for(String im:images) {
					createSteg(inputPath+"\\"+im, outputFolderPath, args[3], LSBs);
					i++;
					System.out.println("Processed "+String.valueOf(i)+" images out of "+String.valueOf(images.length));
				}
				break;
			case "decode":
				decode(inputPath, outputFolderPath);
				break;
			case "batchDecode":
				String[] images2 = new File(inputPath).list(filter);
				int j = 0;
				for(String im:images2) {
					decode(inputPath+"\\"+im, outputFolderPath);
					j++;
					System.out.println("Processed "+String.valueOf(j)+" images out of "+String.valueOf(images2.length));
				}
				break;
			case "prepareDataset":
				String[] percentageStrings = args[5].split(",");
				
				float stegoPercentage = (float) (Float.valueOf(args[6])/100.0);
				String[][] ext = { {"\\train\\stegos","\\train\\cleans"},{"\\valid\\stegos","\\valid\\cleans"},{"\\test\\stegos","\\test\\cleans"}};
				
				for(String[] e1: ext ) {
					for(String e2:e1 ) {
						Files.createDirectories(Paths.get(outputFolderPath+e2));
					}
				}
				
				float[][] percentages = new float[3][2];
				
				for(int k=0; k < 3; k++) {
					float x = (float) (Float.valueOf(percentageStrings[k])/100.0);
					percentages[k][0] = x*stegoPercentage;
					percentages[k][1] = x*(1-stegoPercentage);
				}
				
				
				List<String> stringList = Arrays.asList(new File(inputPath).list(filter));
				Collections.shuffle(stringList);
				String[] toProcess = {};
				toProcess = stringList.toArray(toProcess);
				
				
				int total = toProcess.length;
				int[][] nums = new int[3][2];
				
				
				int running = 0;
				
				for(int a = 0; a < 3; a++) {
					for(int b = 0; b < 2; b++) {
						nums[a][b] = Math.round(total*percentages[a][b]);
						running += nums[a][b];
					}
				}
				
				//Make sure the sum of all the categories is the length
				if(running > total) {
					nums[0][0] = nums[0][0] - (running-total);
				}
				
				
				
				int pointer = 0;
				int done = 0;
				String[] curr;
				for(int a = 0; a < 3; a++) {
					curr = Arrays.copyOfRange(toProcess, pointer, pointer+=nums[a][0]);
					System.out.println(pointer);
					for(String s : curr) {
						try{
							createSteg(inputPath+"\\"+s, outputFolderPath+ext[a][0], args[3], LSBs);
						}catch(Exception e){
							System.out.println("Error on file: "+s);
							e.printStackTrace();
						}
						done++;
						System.out.println("Processed "+String.valueOf(done)+" out of "+String.valueOf(total)+" images.");
					}
					curr = Arrays.copyOfRange(toProcess, pointer, pointer+=nums[a][1]);
					System.out.println(pointer);
					for(String s : curr) {
						try {
							if(LSBs) {
								extractLSBs(inputPath+"\\"+s, outputFolderPath+ext[a][1]+"\\"+s);
							} else {
								Files.copy(Paths.get(inputPath+"\\"+s), Paths.get(outputFolderPath+ext[a][1]+"\\"+s), StandardCopyOption.REPLACE_EXISTING);
							}
						}catch(Exception e) {
							System.out.println("Error on file: "+s);
							e.printStackTrace();
						}
						done++;
						System.out.println("Processed "+String.valueOf(done)+" out of "+String.valueOf(total)+" images.");
					}
				}
			
		}
		
		
	}

}
