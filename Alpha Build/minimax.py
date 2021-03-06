import logging
import random

from igra import IGRALEC_M, IGRALEC_R, PRAZNO, NEODLOCENO, NI_KONEC, nasprotnik

######################################################################
## Algoritem minimax

            # Vrednosti igre
ZMAGA = 10000000 # Mora biti vsaj 10^7
NESKONCNO = ZMAGA + 1 # Več kot zmaga

class Minimax:
    # Algoritem minimax predstavimo z objektom, ki hrani stanje igre in
    # algoritma, nima pa dostopa do GUI (ker ga ne sme uporabljati, saj deluje
    # v drugem vlaknu kot tkinter).

    def __init__(self, globina):
        self.globina = globina  # do katere globine iščemo?
        self.prekinitev = False # ali moramo končati?
        self.igra = None # objekt, ki opisuje igro (ga dobimo kasneje)
        self.jaz = None  # katerega igralca igramo (podatek dobimo kasneje)
        self.poteza = None # sem napišemo potezo, ko jo najdemo


    def prekini(self):
        """Metoda, ki jo pokliče GUI, če je treba nehati razmišljati, ker
           je uporabnik zaprl okno ali izbral novo igro."""
        self.prekinitev = True

    def izracunaj_potezo(self, igra):
        """Izračunaj potezo za trenutno stanje dane igre."""
        # To metodo pokličemo iz vzporednega vlakna
        self.igra = igra
        self.prekinitev = False # Glavno vlakno bo to nastvilo na True, če moramo nehati
        self.jaz = self.igra.na_potezi
        self.poteza = None # Sem napišemo potezo, ko jo najdemo
        # Poženemo minimax
        (poteza, vrednost) = self.minimax(self.globina, True)
        self.jaz = None
        self.igra = None
        if not self.prekinitev:
            # Potezo izvedemo v primeru, da nismo bili prekinjeni
            logging.debug("minimax: poteza {0}, vrednost {1}".format(poteza, vrednost))
            self.poteza = poteza



    def vrednost_pozicije(self):
        """Ocena vrednosti pozicije: sešteje vrednosti vseh trojk na plošči."""
        # Slovar, ki pove, koliko so vredne posamezne trojke, kjer "(x,y) : v" pomeni:
        # če imamo v trojki x znakov igralca in y znakov nasprotnika (in 3-x-y praznih polj),
        # potem je taka trojka za self.jaz vredna v.
        # Trojke, ki se ne pojavljajo v slovarju, so vredne 0.
        vrednost_trojke = {
            (4,0) : ZMAGA,
            (0,4) : -ZMAGA//10,
            (3,0) : ZMAGA//100,
            (0,3) : -ZMAGA//1000,
            (2,0) : ZMAGA//10000,
            (0,2) : -ZMAGA//100000,
            (1,0) : ZMAGA//1000000,
            (0,1) : -ZMAGA//10000000
        }
        vrednost = 0
        for t in self.igra.trojke:
            x = 0
            y = 0
            for (j,i) in t:
                if self.igra.polje[j][i] == self.jaz:
                    x += 1
                elif self.igra.polje[j][i] == nasprotnik(self.jaz):
                    y += 1
            vrednost += vrednost_trojke.get((x,y), 0)
        return vrednost

    def minimax(self, globina, maksimiziramo, alfa = -NESKONCNO, beta = NESKONCNO):
        """Glavna metoda minimax."""
        if self.prekinitev:
            # Sporočili so nam, da moramo prekiniti
            logging.debug ("Minimax prekinja, globina = {0}".format(globina))
            return (None, 0)
        (zmagovalec, lst) = self.igra.stanje_igre()
        if zmagovalec in (IGRALEC_M, IGRALEC_R, NEODLOCENO):
            # Igre je konec, vrnemo njeno vrednost
            if zmagovalec == self.jaz:
                return (None, ZMAGA)
            elif zmagovalec == nasprotnik(self.jaz):
                return (None, -ZMAGA)
            else:
                return (None, 0)
        elif zmagovalec == NI_KONEC:
            # Igre ni konec
            if globina == 0:
                return (None, self.vrednost_pozicije())
            else:
                # Naredimo eno stopnjo minimax
                if maksimiziramo:
                    # Maksimiziramo
                    najboljsa_poteza = None
                    vrednost = -NESKONCNO
                    #print(self.igra.veljavne_poteze())
                    for i, j in self.igra.veljavne_poteze()[::random.choice([1,-1])]:
                        
                        #######UPORABI PRAVO POLJE, DA BO VEDELO V KATERO VRSTICO POVLEČTI POTEZO!!!!#######
                        self.igra.povleci_potezo(i)
                        if vrednost < self.minimax(globina-1, not maksimiziramo, alfa, beta)[1]:
                            najboljsa_poteza = (j, i)
                            vrednost = self.minimax(globina-1, not maksimiziramo, alfa, beta)[1]
                        self.igra.razveljavi()
                        alfa = max(alfa, vrednost)
                        if beta <= alfa:
                            break

                else:
                    # Minimiziramo
                    najboljsa_poteza = None
                    vrednost = NESKONCNO
                    #print(self.igra.veljavne_poteze())
                    for i, j in self.igra.veljavne_poteze()[::random.choice([1,-1])]:
                        self.igra.povleci_potezo(i)
                        if vrednost > self.minimax(globina-1, maksimiziramo, alfa, beta)[1]:
                            najboljsa_poteza = (j, i)
                            vrednost = self.minimax(globina-1, maksimiziramo, alfa, beta)[1]
                        self.igra.razveljavi()
                        beta = min(beta, vrednost)
                        if beta <= alfa:
                            break

                assert (najboljsa_poteza is not None), "minimax: izračunana poteza je None"
                return (najboljsa_poteza, vrednost)
        else:
            assert False, "minimax: nedefinirano stanje igre"
