package main;

public class BotRunner {

	public BotRunner() {
		
	}
	
	public static void main(String[] args) {
        DiscordClient.builder(System.getenv("token"))
                .build()
                .gateway()
                .login()
                .flatMapMany(client -> client.on(MessageCreateEvent.class))
                .filter(event -> event.getGuildId().isPresent())
                .filter(event -> event.getMessage().getContent().startsWith("pingme"))
                .flatMap(ExampleAllowedMentions::sendAllowedMentionsMessage)
                .onErrorContinue((throwable, o) -> throwable.printStackTrace())
                .then()
                .block();
    }

}
