package main;

import discord4j.core.event.domain.message.MessageCreateEvent;
import discord4j.core.object.entity.Message;
import discord4j.core.object.entity.User;
import discord4j.rest.util.AllowedMentions;
import reactor.core.publisher.Mono;

public class BotRunner {

	public BotRunner() {
		
	}
	
	public static void main(String[] args) {
        DiscordClient.builder(System.getenv("NzQ4MDUyOTg0NTU3OTk0MDA0.X0X0oQ.stTetEz3z5lGj8YANXf7mtQxQ-8"))
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
