#include <SPI.h>
#include <TFT_22_ILI9225.h>

#define ENTROPY_PIN 34  
#define BUTTON_PIN  0   

#define TFT_RST 4
#define TFT_RS  2
#define TFT_CS  5   
#define TFT_SDI 23 
#define TFT_CLK 18 
#define TFT_LED -1 

TFT_22_ILI9225 tft = TFT_22_ILI9225(TFT_RST, TFT_RS, TFT_CS, TFT_SDI, TFT_CLK, TFT_LED);

int graphX = 12;         
int prevY = 145;         
bool isPaused = false;   

long statSum = 0;       
long statSumSq = 0;     
int sampleCount = 0;    

#define GRAPH_BASE 170   
#define GRAPH_H 50       
#define GRAPH_W 160      

void setup() {
  pinMode(ENTROPY_PIN, INPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  tft.begin();
  tft.setOrientation(1); 
  tft.setFont(Terminal6x8);
  tft.clear();

  tft.drawText(10, 5, "QUANTUM NOISE SIMULATOR", COLOR_YELLOW);
  tft.drawLine(0, 18, 176, 18, COLOR_GRAY); 
  tft.drawText(10, 30, "8-BIT BINARY:", COLOR_CYAN);
  tft.drawText(10, 70, "DECIMAL:", COLOR_CYAN);
  tft.drawText(85, 70, "Mean:", COLOR_GRAY);
  tft.drawText(85, 80, "Var:", COLOR_GRAY);

  tft.drawRectangle(10, GRAPH_BASE - GRAPH_H - 2, 10 + GRAPH_W, GRAPH_BASE + 2, COLOR_WHITE);
  
  drawStatus();
}

int getRawBit() {
    int noise = analogRead(ENTROPY_PIN);
    return noise & 1; 
}

int getDebiasedBit() {
  while(true) {
    int b1 = getRawBit();
    delayMicroseconds(50); 
    int b2 = getRawBit();
    // Von Neumann Logic:
    if (b1 == 0 && b2 == 1) return 0; 
    if (b1 == 1 && b2 == 0) return 1; 
    delayMicroseconds(50); 
  }
}

byte getQuantumByte() {
  byte result = 0;
  for(int i=0; i<8; i++) {
    int bit = getDebiasedBit(); 
    result = (result << 1) | bit;
  }
  return result;
}

void drawStatus() {
  if (isPaused) {
    tft.fillRectangle(10, 100, 70, 115, COLOR_RED);
    tft.drawText(15, 103, "PAUSED", COLOR_WHITE);
  } else {
    tft.fillRectangle(10, 100, 70, 115, COLOR_GREEN);
    tft.drawText(15, 103, "RUNNING", COLOR_WHITE);
  }
}

void updateStatsDisplay(float mean, float variance) {
  tft.fillRectangle(115, 70, 176, 92, COLOR_BLACK);
  tft.drawText(115, 70, String(mean, 1), COLOR_WHITE);
  tft.drawText(115, 80, String(variance, 0), COLOR_WHITE);
}

void loop() {
  if (digitalRead(BUTTON_PIN) == LOW) {
    delay(50); 
    isPaused = !isPaused;
    drawStatus();
    while(digitalRead(BUTTON_PIN) == LOW); 
  }
  if (isPaused) {
    delay(100);
    return;
  }
  byte qVal = 0;
  do {
    qVal = getQuantumByte();
  } while (qVal == 0); 
  
  statSum += qVal;
  statSumSq += ((long)qVal * qVal);
  sampleCount++;

  if (sampleCount >= 100) {
    float mean = statSum / 100.0;
    float meanSq = statSumSq / 100.0;
    float variance = meanSq - (mean * mean);
    
    updateStatsDisplay(mean, variance);
    
    statSum = 0;
    statSumSq = 0;
    sampleCount = 0;
  }
  String binStr = "";
  for(int i=7; i>=0; i--) binStr += String(bitRead(qVal, i));
  tft.fillRectangle(10, 42, 120, 52, COLOR_BLACK);
  tft.drawText(15, 42, binStr, COLOR_WHITE);
  
  tft.fillRectangle(10, 82, 60, 92, COLOR_BLACK);
  tft.drawText(15, 82, String(qVal), COLOR_GREEN);
  
  int y = map(qVal, 1, 255, 0, GRAPH_H);
  int currentY = GRAPH_BASE - y;
  
  if (graphX > 12) {
      tft.drawLine(graphX - 2, prevY, graphX, currentY, COLOR_GREEN);
  }
  prevY = currentY;
  graphX += 2; 
  if (graphX >= (10 + GRAPH_W - 2)) {
      tft.fillRectangle(11, GRAPH_BASE - GRAPH_H - 1, 9 + GRAPH_W, GRAPH_BASE + 1, COLOR_BLACK);
      graphX = 12; 
      prevY = currentY; 
  }
}