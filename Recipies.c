/* <DESC>
 * Very simple HTTP GET
 * </DESC>
 */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <ctype.h>
#include <curl/curl.h>
#include <unistd.h>

struct MemoryStruct {
  char *memory;
  size_t size;
};

static size_t WriteMemoryCallback(void *contents, size_t size, size_t nmemb, void *userp);
char * find_Ingredients(char * response); 
char * find_Title(char * response);

//******MAIN******//
int main(int argc, char **argv)
{
  CURL *curl;
  CURLcode res;
  // FILE * out = fopen("Recipe.txt","w");
  struct MemoryStruct chunk;
  chunk.memory = malloc(1);  /* will be grown as needed by the realloc at the WriteMemoryCallback function*/
  chunk.size = 0;    /* no data at this point */
  curl = curl_easy_init();
  char * formated_Title = malloc(150);
  char * ingredients_List;

  if(curl) {
    curl_easy_setopt(curl, CURLOPT_URL, argv[argc -1]); // Sets the url to the last given argument
    curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L); // Follows Redirects
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION,WriteMemoryCallback); // Sets the callback function to a function which always increases the memory allocated to our buffer
    curl_easy_setopt(curl, CURLOPT_WRITEDATA,(void*) &chunk); // sets the buffer to which everything is returned to, equal to &chunk instead of stdout
    curl_easy_setopt(curl, CURLOPT_USERAGENT, "libcurl-agent/1.0"); // Gives our request a user agent (some servers prefer it)

    /* Perform the request, res will get the return code */
    res = curl_easy_perform(curl);

    /* Check for errors */
    if(res != CURLE_OK){
      fprintf(stderr, "curl_easy_perform() failed: %s\n",
      curl_easy_strerror(res));
      return 1;
    }
    
    printf("%lu bytes retrieved\n", (unsigned long)chunk.size);
    char * recipe_Title = find_Title(chunk.memory);
    ingredients_List = find_Ingredients(chunk.memory);
    // fprintf(out,"<div class=\"para\"><span style=\"font-size: 20px;\" data-fontsize=\"true\"><a href=\"%s\" rev=\"en_rl_none\" class=\"en-link\"><u>%s</u></a></span></div>\n",argv[argc -1], recipe_Title);
    // sprintf(formated_Title,"<div class=\"para\"><span style=\"font-size: 20px;\" data-fontsize=\"true\"><a href=\"%s\" rev=\"en_rl_none\" class=\"en-link\"><u>%s</u></a></span></div>\n",argv[argc -1], recipe_Title);
    sprintf(formated_Title,"<div><span style=\"font-size: 20px; data-fontsize=true\"><a href=\"%s\" rev=\"en_rl_none class=en-link\"><u>%s</u></a></span></div>\n",argv[argc -1], recipe_Title);
    // fprintf(out,"%s",ingredients_List);
    // printf("%s",ingredients_List);

    /* always cleanup */
    // curl_easy_cleanup(curl);
    // curl_global_cleanup();
    // fclose(out);
    // free(chunk.memory);
    // free(ingredients_List);
    // free(recipe_Title);
  }
  printf("\n");

  char * args[] = {"/usr/bin/python3","./EvernotePy/Add_to_evernote.py",formated_Title,ingredients_List, NULL};
  execv("/usr/bin/python3",args);
  // execlp("/usr/bin/python3","/usr/bin/python3","./EvernotePy/Add_to_evernote.py",formated_Title,ingredients_List, NULL);

  return 0;
}



static size_t
WriteMemoryCallback(void *contents, size_t size, size_t nmemb, void *userp)
{
  size_t realsize = size * nmemb;
  struct MemoryStruct *mem = (struct MemoryStruct *)userp;
 
  char *ptr = realloc(mem->memory, mem->size + realsize + 1);
  if(!ptr) {
    /* out of memory! */
    printf("not enough memory (realloc returned NULL)\n");
    return 0;
  }
 
  mem->memory = ptr;
  memcpy(&(mem->memory[mem->size]), contents, realsize);
  mem->size += realsize;
  mem->memory[mem->size] = 0;
 
  return realsize;
}


char * find_Ingredients(char * response)
{ 
  char string_to_search_for[] =  "recipeIngredient";
  int size = strlen(string_to_search_for);
  char * response_Ingredients = strstr(response,string_to_search_for);
  char * response_Ingredients_end = response_Ingredients;
  char *ingredients_list = malloc(1);
  int ingredients_list_size = 0;
  char * html_div = malloc(256);

  if (response_Ingredients != NULL){
    printf("Found ingredients!\n");
    response_Ingredients += size + 3;
    while (1)
    {
      response_Ingredients_end++;
      if(*response_Ingredients_end == ']')
        break;
    }

    int len = response_Ingredients_end - response_Ingredients;
    char *response_Ingredients_copy = (char*)malloc(sizeof(char)*(len + 1));
    strncpy(response_Ingredients_copy,response_Ingredients,len);
    response_Ingredients_copy[len] = '\0'; 
    
    const char s[2] = "\"";
    char *token;

    /* get the first token */
    token = strtok(response_Ingredients_copy, s);
    int token_size = strlen(token) + 103;
    ingredients_list_size += token_size;
    ingredients_list =  realloc(ingredients_list,ingredients_list_size);     
    ingredients_list[0] = '\0';
   
    /* walk through other tokens */
    while( token != NULL ) {
      ingredients_list_size += strlen(token) + 105;
      ingredients_list = realloc(ingredients_list,ingredients_list_size);     

      if (!strcmp(token,","))
        strcat(ingredients_list,"\n");
      else
      {
        // sprintf(html_div,"<div class=\"para\"><input type=\"checkbox\" checked=\"false\" class=\"en-todo\" contenteditable=\"false\">%s</div>", token);
        sprintf(html_div,"<div><en-todo></en-todo>%s</div>", token);
        strcat(ingredients_list,html_div);
      }

      token = strtok(NULL, s);
    }
    strcat(ingredients_list,"\n");
    free(response_Ingredients_copy);
    return ingredients_list;
  }
  printf("Couldn't find Ingredients\n");
  exit(1);
}


char * find_Title(char * response)
{ 
  char string_to_search_for[] =  "<title>";
  int size = strlen(string_to_search_for);
  char * recipe_Title = strstr(response,string_to_search_for);
  char * recipe_Title_end = recipe_Title;
  char * recipe_Title_copy;

  if (recipe_Title != NULL){
    printf("Found Title!\n");
    recipe_Title += size;
    while (1)
    {
      recipe_Title_end++;
      if(*recipe_Title_end == '<' || *recipe_Title_end == '|')// || strcmp(recipe_Title, "recipe") == 0 || strcmp(recipe_Title, "Recipe") == 0)
        break;
    }

  int len = recipe_Title_end - recipe_Title;
  char * recipe_Title_copy = (char*)malloc(sizeof(char)*(len+1));
  strncpy(recipe_Title_copy,recipe_Title,len);
  recipe_Title_copy[len] = '\0';
  return recipe_Title_copy;
  }
  else
    printf("Didn't Find the Title!\n");
  exit(2);

}