; This is the first program from the BYTE
; article "An Easy Programming System" by
; Joseph Weisbecker. It displays a rocket ship
; sprite pattern on the screen. The article
; only shows the hex values, the source
; statements are re-created. However the
; comments are from the article.
;
; Set V2 = rocket X coordinate = 00
  LD V2, 0
; Set V3 = rocket Y coordinate = 00
  LD V3, 0
; Set I = rocket pattern address = 020A
  LD I, ROCKET
; Display 6 byte rocket pattern
  DRAW V2, V3, 6
; End loop
HERE:  JP HERE
; Rocket pattern byte list
ROCKET:
   DB $..1.....  ; 20
   DB $.111....  ; 70
   DB $.111....  ; 70
   DB $11111...  ; F8
   DB $11.11...  ; D8
   DB $1...1...  ; 88
