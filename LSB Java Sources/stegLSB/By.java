package stegLSB;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.BitSet;



public abstract class By {
	
	//byte[] concatenation
	public static byte[] concat(byte[] first, byte[] second) {
		  byte[] result = Arrays.copyOf(first, first.length + second.length);
		  System.arraycopy(second, 0, result, first.length, second.length);
		  return result;
		}

	
	static BitSet getLSBs(byte[] b) {
		//Extracts the least significant bits from a byte[], returning them as a BitSet
		
		BitSet out = new BitSet();
		int i = 0;
		for(byte curr:b) {
			out.set(i, ((int) curr % 2) != 0);
			i++;
		}
		return out;
	}

	static boolean[] asBits(int n, int encodeSize) {
		boolean[] out = new boolean[encodeSize];
		for(int i = 0; i < encodeSize; i++) {
			out[i] = (n%2 == 1);
			n = n>>1;
		}
		return out;
	}
	
	static int asNum(boolean[] input) {
		int out = 0;
		int exp = 1;
		for(boolean b:input) {
			out += (b?1:0)*exp;
			exp *= 2;
		}
		return out;
	}
	
	static boolean[] asBoolArray(String input) {
		boolean[] out = new boolean[input.length()];
		char[] sC = input.toCharArray();
		for(int i = 0; i < out.length; i++) {
			out[i] = sC[i] == '1';
		}
		return out;
	}
	
	static int asNum(BitSet input) {
		int out = 0;
		int exp = 1;
		for(int i = 0; i < input.length(); i++) {
			out += (input.get(i)?1:0)*exp;
			exp*=2;
		}
		return out;
	}

	static BitSet getHeader(int offset, int fileNameSize, int fileSize) {
		//Encode: offset on 32 bits, fileNameSize on 16 and fileSize on 32, all little-endian, total header size =  80 bits
		BitSet out = new BitSet();
		int pointer = -1;
		
		for(boolean bit : asBits(offset,32)) {
			out.set(pointer+=1, bit);
		}
		for(boolean bit : asBits(fileNameSize,16)) {
			out.set(pointer+=1, bit);
		}
		for(boolean bit : asBits(fileSize,32)) {
			out.set(pointer+=1, bit);
		}
		
		return out;	
	}

	static BitSet getBody(String fileName, byte[] data) {
		byte[] fileNameBin = fileName.getBytes();
		BitSet out = BitSet.valueOf(concat(fileNameBin, data));
		out.set((fileNameBin.length+data.length)*8); //Ensure the last bit of the BitSet is a 1, so we don't lose any trailing zeros
		return out;
	}
	
	static byte[] getFileData(String path) {
		try {
			return Files.readAllBytes(Paths.get(path));
		} catch(Exception e) {
			return new byte[0];
		}
	}

	static void writeFile(String path, byte[] data) throws IOException {
		File file = new File(path);
		
		try{
			FileOutputStream fos = new FileOutputStream(file);
			fos.write(data);
			fos.close();
		}catch(IOException e) {
			file.createNewFile();
			FileOutputStream fos = new FileOutputStream(file);
			fos.write(data);
			fos.close();
		}
		
	}

}
