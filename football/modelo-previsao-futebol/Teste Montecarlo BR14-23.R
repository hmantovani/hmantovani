library(tidyverse)
library(openxlsx)
library(goalmodel)
library(regista)
library(worldfootballR)
library(janitor)
library(magrittr)
library(ggrepel)
library(ggtext)
library(jsonlite)
library(gt)
library(gtExtras)
library(MetBrewer)

# Funções para calcular o resultado da partida
calcV <- function(hg, ag){
  return(hg > ag)
}
calcD <- function(hg, ag){
  return(hg < ag)
}
calcE <- function(hg, ag){
  return(hg == ag)
}
calcPTS <- function(hg, ag){
  return(ifelse(hg < ag, 0, ifelse(hg == ag, 1, 3)))
}
calcTAB <- function(games){
  home <- games %>%
    mutate(casa_V = calcV(hgoal, agoal),
           casa_E = calcE(hgoal, agoal),
           casa_D = calcD(hgoal, agoal),
           casa_PTS = calcPTS(hgoal,agoal)) %>%
    group_by(home) %>% summarise(casa_PTS = sum(casa_PTS),
                                 casa_J = length(home),
                                 casa_V = sum(casa_V),
                                 casa_E = sum(casa_E),
                                 casa_D = sum(casa_D),
                                 casa_GP = sum(as.numeric(hgoal)),
                                 casa_GS = sum(as.numeric(agoal)),
                                 casa_SG = sum(as.numeric(hgoal)) - sum(as.numeric(agoal))) %>%
    dplyr::rename(Time = home)
  
  away <- games %>%
    mutate(fora_V = calcV(agoal, hgoal),
           fora_E = calcE(agoal, hgoal),
           fora_D = calcD(agoal, hgoal),
           fora_PTS = calcPTS(agoal,hgoal)) %>%
    group_by(away) %>% summarise(fora_PTS = sum(fora_PTS),
                                 fora_J = length(away),
                                 fora_V = sum(fora_V),
                                 fora_E = sum(fora_E),
                                 fora_D = sum(fora_D),
                                 fora_GP = sum(as.numeric(agoal)),
                                 fora_GS = sum(as.numeric(hgoal)),
                                 fora_SG = sum(as.numeric(agoal)) - sum(as.numeric(hgoal))) %>%
    dplyr::rename(Time = away)
  
  total <- inner_join(home, away, by = 'Time') %>%
    mutate(PTS = casa_PTS + fora_PTS,
           J = casa_J + fora_J,
           V = casa_V + fora_V,
           E = casa_E + fora_E,
           D = casa_D + fora_D,
           GP = casa_GP + fora_GP,
           GS = casa_GS + fora_GS,
           SG = casa_SG + fora_SG) %>%
    select(Time, PTS, J, V, E, D, GP, GS, SG) %>%
    arrange(desc(PTS), desc(V), desc(SG), desc(GP)) %>%
    mutate(Pos = row_number()) %>%
    relocate(Pos) %>%
    mutate(AP = round(PTS / (J * 3) * 100, digits = 1))
  
  return(total)
}

folder = "C:/R/Simuladores BR 2023/"
current_date <- strftime(Sys.Date(), format = "%d-%m-%Y")
excel <- createWorkbook()
tabelas_reais <- list()
tabelas_sim <- list()

camcorder::gg_record(
  dir = file.path(here::here("camcorder_outputs")),
  device = "png",
  width = 18,
  height = 10,
  dpi = 300)
sysfonts::font_add_google(name = "IBM Plex Sans", family = "IBM")
showtext::showtext_auto()
showtext::showtext_opts(dpi = 300)
font <- "IBM"

for(year in 2014:2022){
  data <- fb_match_results(country = "BRA",
                           gender = "M",
                           season_end_year = year,
                           tier = "1st") %>%
    clean_names() %>% factor_teams(c("home", "away")) %>% 
    rename(hgoal = home_goals, agoal = away_goals) %>% 
    select('wk', 'date', 'home', 'away', 'hgoal', 'agoal')
  data$wk <- as.numeric(data$wk)

  train_data <- data %>% subset(wk < 20) %>% select(-wk)
  test_data <- data %>% subset(wk > 19) %>% select(-wk) %>% mutate(hgoal = NA, agoal = NA)
  
  # Dataframe vazio para armazenar todas tabelas finais
  montecarlo_tabelas <- setNames(data.frame(matrix(ncol = 12, nrow = 0)),
                                 c('Pos', 'Time', 'PTS', 'J', 'V', 'E',
                                   'D', 'GP', 'GS', 'SG', 'AP', 'sim'))
  montecarlo_tabelas_df <- list()
  
  # Dataframe vazio para armazenar todos os jogos
  montecarlo_jogos <- setNames(data.frame(matrix(ncol = 10, nrow = 0)),
                               c('year', 'home', 'hgoal', 'agoal', 'away',
                                 'p1', 'pX', 'p2', 'hxg', 'axg'))
  montecarlo_jogos_df <- list()
  
  pesos <- weights_dc(train_data$date, xi = 0.0025)
  model <- goalmodel(goals1 = train_data$hgoal,
                     goals2 = train_data$agoal,
                     team1 = train_data$home,
                     team2 = train_data$away,
                     dc = TRUE,
                     rs = TRUE,
                     model = 'poisson',
                     weights = pesos)
  
  # Quantidade de simulações
  runs = 10
  
  for(n in 1:runs){
    run <- test_data
    run$p1 <- NA
    run$pX <- NA
    run$p2 <- NA
    run$hxg <- NA
    run$axg <- NA
    
    for(i in 1:nrow(run)){
      plac <- predict_goals(
        model,
        team1 = run$home[i],
        team2 = run$away[i],
        return_df = TRUE,
        maxgoal = 15)
      plac$res <- paste(plac$goals1,plac$goals2,sep="x")
      plac <- plac[c(1,2,5,6)]
      plac$probability <- ifelse(plac$probability < 0,
                                 abs(plac$probability), plac$probability)
      
      match <- sample(plac$res, 1, prob = plac$probability)
      match <- data.frame(test_data$date[i], test_data$home[i],
                          test_data$away[i], match)
      colnames(match) <- c('date', 'home', 'away', 'x')
      match[c('hgoal', 'agoal')] <- str_split_fixed(match$x, 'x', 2)
      match$x <- 'x'
      match <- match[c(1,2,5,6,3)]
      
      suppressWarnings({
        xg <- predict_expg(
          model,
          team1 = run$home[i],
          team2 = run$away[i],
          return_df = TRUE)
      })
      
      suppressWarnings({
        pro <- predict_result(
          model,
          team1 = run$home[i],
          team2 = run$away[i],
          return_df = TRUE)
        
        pro$p1 <- ifelse(pro$p1 < 0, abs(pro$p1), pro$p1)
        pro$pd <- ifelse(pro$pd < 0, abs(pro$pd), pro$pd)
        pro$p2 <- ifelse(pro$p2 < 0, abs(pro$p2), pro$p2)
        sum_prob <- pro$p1 + pro$pd + pro$p2
        pro$p1 <- 1 / sum_prob * pro$p1
        pro$pd <- 1 / sum_prob * pro$pd
        pro$p2 <- 1 / sum_prob * pro$p2
      })
      
      match$p1 <- pro$p1
      match$pX <- pro$pd
      match$p2 <- pro$p2
      match$hxg <- xg$expg1
      match$axg <- xg$expg2
      run <- rbind(run,match)
    }
    
    run <- run %>% drop_na(hgoal)
    simmed <- run %>% select(1,2,3,4,5)
    total <- rbind(train_data, simmed)
    
    classificacao_casa <- total %>%
      mutate(casa_V = calcV(hgoal, agoal),
             casa_E = calcE(hgoal, agoal),
             casa_D = calcD(hgoal, agoal),
             casa_PTS = calcPTS(hgoal,agoal)) %>%
      group_by(home) %>% summarise(casa_PTS = sum(casa_PTS),
                                   casa_J = length(home),
                                   casa_V = sum(casa_V),
                                   casa_E = sum(casa_E),
                                   casa_D = sum(casa_D),
                                   casa_GP = sum(as.numeric(hgoal)),
                                   casa_GS = sum(as.numeric(agoal)),
                                   casa_SG = sum(as.numeric(hgoal)) - sum(as.numeric(agoal))) %>%
      dplyr::rename(Time = home)
    
    classificacao_fora <- total %>%
      mutate(fora_V = calcV(agoal, hgoal),
             fora_E = calcE(agoal, hgoal),
             fora_D = calcD(agoal, hgoal),
             fora_PTS = calcPTS(agoal,hgoal)) %>%
      group_by(away) %>% summarise(fora_PTS = sum(fora_PTS),
                                   fora_J = length(away),
                                   fora_V = sum(fora_V),
                                   fora_E = sum(fora_E),
                                   fora_D = sum(fora_D),
                                   fora_GP = sum(as.numeric(agoal)),
                                   fora_GS = sum(as.numeric(hgoal)),
                                   fora_SG = sum(as.numeric(agoal)) - sum(as.numeric(hgoal))) %>%
      dplyr::rename(Time = away)
    
    classificacao_final <- inner_join(classificacao_casa, classificacao_fora, by = 'Time') %>%
      mutate(PTS = casa_PTS + fora_PTS,
             J = casa_J + fora_J,
             V = casa_V + fora_V,
             E = casa_E + fora_E,
             D = casa_D + fora_D,
             GP = casa_GP + fora_GP,
             GS = casa_GS + fora_GS,
             SG = casa_SG + fora_SG) %>%
      select(Time, PTS, J, V, E, D, GP, GS, SG) %>%
      arrange(desc(PTS), desc(V), desc(SG), desc(GP)) %>%
      mutate(Pos = row_number()) %>%
      relocate(Pos) %>%
      mutate(AP = round(PTS / (J * 3) * 100, digits = 1)) %>%
      mutate(sim = n)
    
    montecarlo_tabelas <- do.call(rbind, list(montecarlo_tabelas, classificacao_final))
    montecarlo_tabelas_df <- c(montecarlo_tabelas_df, list(classificacao_final))
    run <- run %>% mutate(sim = n)
    montecarlo_jogos <- do.call(rbind, list(montecarlo_jogos, run))
    montecarlo_jogos_df <- c(montecarlo_jogos_df, list(run))
  }
  
  # Montar classificação média
  tabela_real <- calcTAB(data) %>% select(-AP) %>% mutate(ano=year)
  tabela_sim <- montecarlo_tabelas %>% group_by(Time) %>%
    summarise(PTS = round(mean(PTS)),
              J = round(mean(J)),
              V = round(mean(V)),
              E = round(mean(E)),
              D = round(mean(D)),
              GP = round(mean(GP)),
              GS = round(mean(GS)),
              SG = round(mean(SG))) %>%
    arrange(desc(PTS), desc(V), desc(SG), desc(GP)) %>%
    mutate(Pos = row_number()) %>%
    relocate(Pos) %>% mutate(ano=year)
  
  tabelas_reais <- c(tabelas_reais, list(tabela_real))
  tabelas_sim <- c(tabelas_sim, list(tabela_sim))
}

real <- bind_rows(tabelas_reais)
sim <- bind_rows(tabelas_sim)

addWorksheet(excel, "Real")
addWorksheet(excel, "Sim")
writeData(excel, sheet = "Real", x = real, rowNames=TRUE)
writeData(excel, sheet = "Sim", x = sim, rowNames=TRUE)
saveWorkbook(excel, overwrite=TRUE, paste(folder, '14-22.xlsx', sep = ''))